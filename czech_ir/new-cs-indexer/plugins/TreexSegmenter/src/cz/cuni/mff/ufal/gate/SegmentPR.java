package cz.cuni.mff.ufal.gate;

import cz.cuni.mff.ufal.treex.Segmenter;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.MalformedURLException;
import java.net.URL;
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
	URL perlSegmenterPath;
	
	/**
	 * @return the perlSegmenterPath
	 */
	public URL getPerlSegmenterPath() {
		return perlSegmenterPath;
	}

	/**
	 * @param perlSegmenterPath the perlSegmenterPath to set
	 */
	@CreoleParameter(comment = "a path to the Perl segmenter",
			defaultValue = "scripts")
	public void setPerlSegmenterPath(URL perlSegmenterPath) {
		this.perlSegmenterPath = perlSegmenterPath;
	}

	Segmenter segmenter;
	
	public Resource init() throws ResourceInstantiationException {
		try {
			this.segmenter = new Segmenter(perlSegmenterPath.getPath());
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
//		try {
//			File f = new File(perlSegmenterPath.getPath(), "skuska1");
//			PrintWriter out = new PrintWriter(f);
//			out.print(text);
//			out.close();
//		} catch (FileNotFoundException e1) {
//			// TODO Auto-generated catch block
//			e1.printStackTrace();
//		}
		
//		System.err.printf("SENTENCES: %s", sents.size());
		char[] textChar = text.toCharArray();
		int startPos = 0;
		for (String sent : sents) {
			if (sent.isEmpty()) {
				continue;
			}
			int endPos = alignTextWithSent(textChar, startPos, sent);
			try {
				morphoAnnot.add((long) startPos, (long) endPos, "Sentence", Factory.newFeatureMap());
			} catch (InvalidOffsetException e) {
				throw new ExecutionException();
			}
			startPos = endPos;
		}
		
	}
	
	private int alignTextWithSent(char[] textChar, int textPos, String sent) {
		int sentLen = sent.length();
		char[] sentChar = sent.toCharArray();
		int sentPos = 0;
		while (textPos < textChar.length && sentPos < sentLen) {
			while (textPos < textChar.length && Character.isWhitespace(textChar[textPos])) {
				textPos++;
//				System.err.printf("tp_ws: %d\n", textPos);
			}
			while (sentPos < sentLen && Character.isWhitespace(sentChar[sentPos])) {
				sentPos++;
//				System.err.printf("sp_ws: %d\n", textPos);
			}
			textPos++;
			sentPos++;
		}
		return textPos;
	}
	
	public static void main(String[] args) {
		SegmentPR segmenter = new SegmentPR();
		try {
			segmenter.setPerlSegmenterPath(new URL("scripts"));
		} catch (MalformedURLException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
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
