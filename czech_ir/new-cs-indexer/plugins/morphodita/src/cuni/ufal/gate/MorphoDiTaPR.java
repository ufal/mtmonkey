package cuni.gate;

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

@SuppressWarnings("serial")
@CreoleResource(name = "Czech sentence segmenter")
public class MorphoDiTaPR extends AbstractLanguageAnalyser {
	
	/** Init-time parameters */
	private String taggerModelPath;
	
	/**
	 * @return the perlSegmenterPath
	 */
	public String getTaggerModelPath() {
		return taggerModelPath;
	}

	/**
	 * @param perlSegmenterPath the perlSegmenterPath to set
	 */
	@CreoleParameter(comment = "path to a model for MorphoDiTa tagger")
	public void setTaggerModelPath(String taggerModelPath) {
		this.taggerModelPath = taggerModelPath;
	}
	
	/** Run-time parameters */
	private boolean fromRawText = false;
	
	/**
	 * @return the fromRawText
	 */
	public boolean isFromRawText() {
		return fromRawText;
	}

	/**
	 * @param fromRawText the fromRawText to set
	 */
	public void setFromRawText(boolean fromRawText) {
		this.fromRawText = fromRawText;
	}

	Tagger tagger = null;
	
	public Resource init() throws ResourceInstantiationException {
		this.tagger = Tagger.load(this.taggerModelPath);
		if (tagger == null)
			throw new ResourceInstantiationException();
		return this;
	}

	public void execute() throws ExecutionException {
		if (isFromRawText()) {
			try {
				tagUntokenized();
			} catch (InvalidOffsetException e) {
				throw new ExecutionException();
			}
		}
		else {
		}
	}
	
public void tagUntokenized() throws InvalidOffsetException {

	Tokenizer tokenizer = this.tagger.newTokenizer();
	Forms forms = new Forms();
    TaggedLemmas taggedLemmas = new TaggedLemmas();
    TokenRanges tokens = new TokenRanges();
	
	String text = document.getContent().toString();
	AnnotationSet morphoAnnot = document.getAnnotations("Morpho");
	
	tokenizer.setText(text);
	
	long t = 0;
	while (tokenizer.nextSentence(forms, tokens)) {
		this.tagger.tag(forms, taggedLemmas);
		for (int i = 0; i < taggedLemmas.size(); i++) {
			TaggedLemma taggedLemma = taggedLemmas.get(i);
			TokenRange token = tokens.get(i);
			long tokenStart = token.getStart();
			long tokenEnd = token.getStart() + token.getLength();
			
			morphoAnnot.add(t, tokenStart, "SpaceToken", Factory.newFeatureMap());
			
			FeatureMap morphoFeats = Factory.newFeatureMap();
			morphoFeats.put("lemma", taggedLemma.getLemma());
			morphoFeats.put("tag", taggedLemma.getTag());
			morphoAnnot.add(tokenStart, tokenEnd, "SpaceToken", Factory.newFeatureMap());
			
			t = tokenEnd;
		}
	}
}

}