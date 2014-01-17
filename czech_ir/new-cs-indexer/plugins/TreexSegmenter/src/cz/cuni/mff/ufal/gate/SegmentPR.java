package cz.cuni.mff.ufal.gate;

import cz.cuni.mff.ufal.treex.Segmenter;

import java.io.File;
import java.io.IOException;
import java.util.List;

import gate.AnnotationSet;
import gate.Factory;
import gate.Resource;
import gate.creole.AbstractLanguageAnalyser;
import gate.creole.ExecutionException;
import gate.creole.ResourceInstantiationException;
import gate.creole.metadata.CreoleResource;
import gate.creole.metadata.CreoleParameter;
import gate.util.InvalidOffsetException;

@SuppressWarnings("serial")
@CreoleResource(name = "Czech sentence segmenter")
public class SegmentPR extends AbstractLanguageAnalyser {
	
	/** Init-time parameters */
	String perlSegmenterPath;
	
	/**
	 * @return the perlSegmenterPath
	 */
	public String getPerlSegmenterPath() {
		return perlSegmenterPath;
	}

	/**
	 * @param perlSegmenterPath the perlSegmenterPath to set
	 */
	@CreoleParameter(comment = "a path to the Perl segmenter",
			defaultValue = "scripts")
	public void setPerlSegmenterPath(String perlSegmenterPath) {
		this.perlSegmenterPath = perlSegmenterPath;
	}

	Segmenter segmenter;
	
	public Resource init() throws ResourceInstantiationException {
		try {
			this.segmenter = new Segmenter(perlSegmenterPath);
			return this;
		} catch (IOException e) {
			try {
				throw new ResourceInstantiationException((new File(".")).getCanonicalPath());
			} catch (IOException e1) {
				throw new ResourceInstantiationException(e);
			}
		}
	}
	
	public void execute() throws ExecutionException {
		String text = document.getContent().toString();
		AnnotationSet morphoAnnot = document.getAnnotations("Morpho");
		List<String> sents;
		try {
			sents = this.segmenter.process_text(text);
		} catch (IOException e) {
			throw new ExecutionException();
		}
		long pos = 0;
		for (int i = 0; i < sents.size(); i++) {
			String sent = sents.get(i);
			try {
				morphoAnnot.add(pos, pos + sent.length(), "Sentence", Factory.newFeatureMap());
			} catch (InvalidOffsetException e) {
				throw new ExecutionException();
			}
			pos += sent.length();
		}
		
	}
	
	public static void main(String[] args) {
		SegmentPR segmenter = new SegmentPR();
		segmenter.setPerlSegmenterPath("scripts");
		try {
			segmenter.init();
		} catch (ResourceInstantiationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		try {
			segmenter.execute();
		} catch (ExecutionException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
}
