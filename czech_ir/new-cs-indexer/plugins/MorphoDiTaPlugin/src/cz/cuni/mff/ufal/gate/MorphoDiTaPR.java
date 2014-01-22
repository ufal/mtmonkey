package cz.cuni.mff.ufal.gate;

import java.net.URL;
import java.util.List;
import java.util.Scanner;

import cz.cuni.mff.ufal.morphodita.Forms;
import cz.cuni.mff.ufal.morphodita.TaggedLemma;
import cz.cuni.mff.ufal.morphodita.TaggedLemmas;
import cz.cuni.mff.ufal.morphodita.Tagger;
import cz.cuni.mff.ufal.morphodita.TokenRange;
import cz.cuni.mff.ufal.morphodita.TokenRanges;
import cz.cuni.mff.ufal.morphodita.Tokenizer;
import gate.AnnotationSet;
import gate.Factory;
import gate.FeatureMap;
import gate.Resource;
import gate.creole.AbstractLanguageAnalyser;
import gate.creole.ExecutionException;
import gate.creole.ResourceInstantiationException;
import gate.creole.metadata.CreoleParameter;
import gate.creole.metadata.CreoleResource;
import gate.util.InvalidOffsetException;


@CreoleResource(name = "Czech tagger, morphology, tokenizer and sentence splitter")
public class MorphoDiTaPR extends AbstractLanguageAnalyser {
	
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
	 * @param fromRawText the fromRawText to set
	 */
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
	//	if (Boolean.valueOf(getFromRawText())) {
			try {
				tagUntokenized();
			} catch (InvalidOffsetException e) {
				throw new ExecutionException(e);
			}
	//	}
	//	else {
	//	}
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
	
	private void addToken(AnnotationSet annot, TaggedLemma taggedLemma, long start, long end, boolean isLast) throws InvalidOffsetException {
		FeatureMap tokenFeats = Factory.newFeatureMap();
		tokenFeats.put("lemma", taggedLemma.getLemma());
		tokenFeats.put("tag", taggedLemma.getTag());
		//System.err.printf("TOKEN: %d, %d\n", tokenStart, tokenEnd);
		annot.add(start, end, "Token", tokenFeats);
		if (isLast && taggedLemma.getTag().startsWith("Z")) {
			FeatureMap splitFeats = Factory.newFeatureMap();
			splitFeats.put("kind", "internal");
			//System.err.printf("TOKEN: %d, %d\n", tokenStart, tokenEnd);
			annot.add(start, end, "Split", splitFeats);
		}
	}
	
	private void addSentence(AnnotationSet annot, long start, long end) throws InvalidOffsetException {
		annot.add(start, end, "Sentence", Factory.newFeatureMap());
	}
	
	private void tagUntokenized() throws InvalidOffsetException {	
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
					
					addToken(morphoAnnot, taggedLemma, tokenStart, tokenEnd, i == taggedLemmas.size()-1);
					
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
	
}