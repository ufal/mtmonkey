package cz.cuni.mff.ufal.gate;

import java.net.URL;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Scanner;

import cz.cuni.mff.ufal.morphodita.Forms;
import cz.cuni.mff.ufal.morphodita.TaggedLemma;
import cz.cuni.mff.ufal.morphodita.TaggedLemmas;
import cz.cuni.mff.ufal.morphodita.Tagger;
import cz.cuni.mff.ufal.morphodita.TokenRange;
import cz.cuni.mff.ufal.morphodita.TokenRanges;
import cz.cuni.mff.ufal.morphodita.Tokenizer;
import gate.Annotation;
import gate.AnnotationSet;
import gate.Factory;
import gate.FeatureMap;
import gate.Resource;
import gate.creole.AbstractLanguageAnalyser;
import gate.creole.ExecutionException;
import gate.creole.ResourceInstantiationException;
import gate.creole.metadata.CreoleParameter;
import gate.creole.metadata.CreoleResource;
import gate.creole.metadata.RunTime;
import gate.util.InvalidOffsetException;


@CreoleResource(name = "Czech tagger, morphology, tokenizer and sentence splitter")
public class MorphoDiTaPR extends AbstractLanguageAnalyser {
	
	private final class TextRange {
		private long start;
		private long end;
		
		public TextRange(long start, long end) {
			this.start = start;
			this.end = end;
		}
		
		public long getStart() {
			return start;
		}
		public long getEnd() {
			return end;
		}
	}
	
	private class SentenceIterator {
		
		private List<Annotation> sentAnnotList;
		private Iterator<Annotation> sentAnnotIterator;
		
		public SentenceIterator(AnnotationSet annot) {
			this.sentAnnotList = new ArrayList<Annotation>(annot);
			Collections.sort(sentAnnotList, new gate.util.OffsetComparator());
			this.sentAnnotIterator = sentAnnotList.iterator();
		}
		
		public boolean hasNextSentence() {
			return sentAnnotIterator.hasNext();
		}
		
		public TextRange nextSentence() {
			Annotation a = sentAnnotIterator.next();
			long start = a.getStartNode().getOffset();
			long end = a.getEndNode().getOffset();
			TextRange sentRange = new TextRange(start, end);
			return sentRange;
		}
	}
	
	/**
	 * 
	 */
	private static final long serialVersionUID = -4636237986378212943L;
	/** Init-time parameters */
	private URL taggerModelPath;
	
	/**
	 * @return the perlSegmenterPath
	 */
	public URL getTaggerModelPath() {
		return taggerModelPath;
	}

	/**
	 * @param perlSegmenterPath the perlSegmenterPath to set
	 */
	@CreoleParameter(comment = "path to a model for MorphoDiTa tagger",
			defaultValue = "morphodita/models/czech-131023.tagger-best_accuracy")
	public void setTaggerModelPath(URL taggerModelPath) {
		this.taggerModelPath = taggerModelPath;
	}
	
	/** Run-time parameters */
	private String splitSentences;
	
	/**
	 * @return the splitSentences
	 */
	public String getSplitSentences() {
		return splitSentences;
	}

	/**
	 * @param splitSentences the splitSentences to set
	 */
	@RunTime
	@CreoleParameter(comment = "Carry out sentence splitting",
			defaultValue = "false")
	public void setSplitSentences(String splitSentences) {
		this.splitSentences = splitSentences;
	}

	Tagger tagger = null;
	
	public Resource init() throws ResourceInstantiationException {
		this.tagger = Tagger.load(this.taggerModelPath.getPath());
		if (tagger == null)
			throw new ResourceInstantiationException();
		return this;
	}

	public void execute() throws ExecutionException {
		try {
			if (Boolean.valueOf(splitSentences)) {
				tagUnsegmented();
			}
			else {
				tagSegmented();
			}
		}
		catch (InvalidOffsetException e) {
			throw new ExecutionException();
		}
	}
	
	
	private void addSpace(AnnotationSet annot, long start, long end) throws InvalidOffsetException {
		FeatureMap morphoFeats = Factory.newFeatureMap();
		morphoFeats.put("kind", "space");
		annot.add(start, end, "SpaceToken", morphoFeats);
	}
	
	private void addNewline(AnnotationSet annot, long start, long end) throws InvalidOffsetException {
		FeatureMap splitFeats = Factory.newFeatureMap();
		splitFeats.put("kind", "external");
		annot.add(start, end, "Split", splitFeats);
		FeatureMap tokenFeats = Factory.newFeatureMap();
		tokenFeats.put("kind", "control");
		annot.add(start, end, "SpaceToken", tokenFeats);
	}
	
	private void addToken(AnnotationSet annot, TaggedLemma taggedLemma, long start, long end) throws InvalidOffsetException {
		FeatureMap tokenFeats = Factory.newFeatureMap();
		tokenFeats.put("form", document.getContent().getContent(start, end).toString());
		tokenFeats.put("lemma", taggedLemma.getLemma());
		tokenFeats.put("tag", taggedLemma.getTag());
		//System.err.printf("TOKEN: %d, %d\n", tokenStart, tokenEnd);
		annot.add(start, end, "Token", tokenFeats);
//		if (isLast && taggedLemma.getTag().startsWith("Z")) {
//			FeatureMap splitFeats = Factory.newFeatureMap();
//			splitFeats.put("kind", "internal");
//			//System.err.printf("TOKEN: %d, %d\n", tokenStart, tokenEnd);
//			annot.add(start, end, "Split", splitFeats);
//		}
	}
	
	private void addSentence(AnnotationSet annot, long start, long end) throws InvalidOffsetException {
		annot.add(start, end, "Sentence", Factory.newFeatureMap());
	}
	
	private void tagUnsegmented() throws InvalidOffsetException {	
		Tokenizer tokenizer = this.tagger.newTokenizer();
		Forms forms = new Forms();
	    TaggedLemmas taggedLemmas = new TaggedLemmas();
	    TokenRanges tokens = new TokenRanges();
		
		String text = document.getContent().toString();
		AnnotationSet morphoAnnot = document.getAnnotations("Morpho");
//		try {
//			File f = new File("/home/mnovak/projects/khresmoi-mt/czech_ir/new-cs-indexer/plugins/MorphoDiTaPlugin/morphodita/bindings/java/examples/text.txt");
//			PrintWriter out = new PrintWriter(f);
//			out.print(text);
//			out.close();
//		} catch (FileNotFoundException e1) {
//			// TODO Auto-generated catch block
//			e1.printStackTrace();
//		}
		Scanner reader = new Scanner(text);
		
		long lineStart = 0;
		while (reader.hasNextLine()) {
			String line = reader.nextLine();
			//System.err.println("LINE: " + line);
			tokenizer.setText(line);
			long sentStart = lineStart;
			//System.err.printf("SENT_START: %d\n", sentStart);
			while (tokenizer.nextSentence(forms, tokens)) {
				this.tagger.tag(forms, taggedLemmas);
				long wsStart = sentStart;
				for (int i = 0; i < taggedLemmas.size(); i++) {
					TaggedLemma taggedLemma = taggedLemmas.get(i);
					TokenRange token = tokens.get(i);
					long tokenStart = lineStart + token.getStart();
					long tokenEnd = tokenStart + token.getLength();
					if (i == 0) {
						sentStart = tokenStart;
					}
					
					//System.err.printf("SPACE_TOKEN: %d, %d\n", wsStart, tokenStart-1);					
					if (wsStart < tokenStart) {
						addSpace(morphoAnnot, wsStart, tokenStart);
					}
					
					addToken(morphoAnnot, taggedLemma, tokenStart, tokenEnd);
					
					wsStart = tokenEnd;
				}	
				//System.err.printf("SENT: %d, %d\n", sentStart, wsStart);
				addSentence(morphoAnnot, sentStart, wsStart);
				sentStart = wsStart;
			}
			long lineEnd = lineStart + line.length();
			//System.err.printf("SPACE_TOKEN: %d, %d\n", sentStart, lineEnd);
			if (sentStart < lineEnd) {
				addSpace(morphoAnnot, sentStart, lineEnd);
			}
			lineStart = lineEnd + 1;
			//System.err.printf("SPLIT: %d, %d\n", lineEnd, lineStart);
			addNewline(morphoAnnot, lineEnd, lineStart);
			
		}
	}
	
	private void tagSegmented() throws InvalidOffsetException {
		Tokenizer tokenizer = this.tagger.newTokenizer();
		Forms forms = new Forms();
	    TaggedLemmas taggedLemmas = new TaggedLemmas();
	    TokenRanges tokens = new TokenRanges();
		
		AnnotationSet morphoAnnot = document.getAnnotations("Morpho");
		SentenceIterator sentIter = new SentenceIterator(morphoAnnot);
		
		while (sentIter.hasNextSentence()) {
			TextRange sentRange = sentIter.nextSentence();
			long sentStart = sentRange.getStart();
			long sentEnd = sentRange.getEnd();
			String sent = document.getContent().getContent(sentStart, sentEnd).toString();
			tokenizer.setText(sent);
			
			long currPos = sentStart;
			//System.err.printf("SENT_START: %d\n", sentStart);
			while (tokenizer.nextSentence(forms, tokens)) {
				this.tagger.tag(forms, taggedLemmas);
				for (int i = 0; i < taggedLemmas.size(); i++) {
					TaggedLemma taggedLemma = taggedLemmas.get(i);
					TokenRange token = tokens.get(i);
					long tokenStart = sentStart + token.getStart();
					long tokenEnd = tokenStart + token.getLength();
					
					//System.err.printf("SPACE_TOKEN: %d, %d\n", wsStart, tokenStart-1);					
					if (currPos < tokenStart) {
						addSpace(morphoAnnot, currPos, tokenStart);
					}
					
					addToken(morphoAnnot, taggedLemma, tokenStart, tokenEnd);
					
					currPos = tokenEnd;
				}	
			}
		}

	}
	
}