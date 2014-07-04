package cz.cuni.mff.ufal.gate;

import cz.cuni.mff.ufal.treex.Segmenter;

import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.List;

import gate.AnnotationSet;
import gate.Factory;
import gate.FeatureMap;
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
		try {
			annotateSentences(text, morphoAnnot);
		} catch (Exception e) {
			throw new ExecutionException(e);
		}
	}
	
	public void annotateSentences(String text, AnnotationSet annot) throws InvalidOffsetException, IOException {
		boolean withExternalSplits = true;
		List<String> sents;
		sents = this.segmenter.process_text(text, withExternalSplits);

//		try {
//			File f = new File(perlSegmenterPath.getPath(), "skuska1");
//			PrintWriter out = new PrintWriter(f);
//			out.print(StringUtils.join(sents, "\n"));
//			out.close();
//		} catch (FileNotFoundException e1) {
//			// TODO Auto-generated catch block
//			e1.printStackTrace();
//		}
		
//		System.err.printf("SENTENCES: %s", sents.size());
		char[] textChar = text.toCharArray();
		int startPos = 0;
		for (String sent : sents) {
			//System.err.printf("SENT: %s\n", sent);
			if (sent.isEmpty()) {
				continue;
			}
			while (startPos < textChar.length && Character.isWhitespace(textChar[startPos]) && textChar[startPos] != '\n') {
				annot.add((long) startPos, (long) startPos+1, "SpaceToken", Factory.newFeatureMap());
				startPos++;
				//System.err.printf("tp_ws: %d\n", startPos);
			}
			int endPos;
			if (sent.equals(Segmenter.EXTERNAL_SPLIT)) {
				endPos = startPos + 1;
				FeatureMap feats = Factory.newFeatureMap();
				feats.put("kind", "external");
				//System.err.printf("SPLIT: (%d, %d)\n", startPos, endPos);
				annot.add((long) startPos, (long) endPos, "Split", feats);
			}
			else {
				endPos = alignTextWithSent(textChar, startPos, sent);
				//System.err.printf("SENT: (%d, %d)\n", startPos, endPos);
				annot.add((long) startPos, (long) endPos, "Sentence", Factory.newFeatureMap());
			}
			startPos = endPos;
		}
		//System.err.println("DOC_END");
	}
	
	private int alignTextWithSent(char[] textChar, int textPos, String sent) {
		char[] sentChar = sent.toCharArray();
		int sentPos = 0;
		while (textPos < textChar.length && sentPos < sentChar.length) {
			while (textPos < textChar.length && Character.isWhitespace(textChar[textPos])) {
				textPos++;
//				System.err.printf("tp_ws: %d\n", textPos);
			}
			while (sentPos < sentChar.length && Character.isWhitespace(sentChar[sentPos])) {
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
