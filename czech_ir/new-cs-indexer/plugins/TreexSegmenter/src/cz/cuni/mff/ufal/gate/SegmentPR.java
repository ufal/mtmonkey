package cz.cuni.mff.ufal.gate;

import cz.cuni.mff.ufal.treex.Segmenter;

import java.io.IOException;
import java.util.List;

import gate.Resource;
import gate.creole.AbstractLanguageAnalyser;
import gate.creole.ExecutionException;
import gate.creole.ResourceInstantiationException;
import gate.creole.metadata.CreoleResource;
import gate.creole.metadata.CreoleParameter;

@SuppressWarnings("serial")
@CreoleResource(name = "Czech sentence segmenter")
public class SegmentPR extends AbstractLanguageAnalyser {
	
	public String text = "";
	
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
			throw new ResourceInstantiationException();
		}
	}
	
	public void execute() throws ExecutionException {
		try {
			List<String> sents = this.segmenter.process_text(this.text);
			long pos = 0;
			for (int i = 0; i < sents.size(); i++) {
				String sent = sents.get(i);
				long start_pos = pos;
				long end_pos = pos + sents.get(i).length();
				System.out.printf("(%d, %d): %s\n", start_pos, end_pos, sent);
				pos += sent.length();
			}
		} catch (IOException e) {
			throw new ExecutionException();
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
		segmenter.text = "Jako šéf ODS předsedal dvěma vládám v letech 1992 až 1997. " +
				"První vláda samostatné ČR (2. července 1992 - 4. července 1996; demise 2. července 1996) " +
				"byla jmenována ještě v době federace a tvořili ji ministři za ODS, KDU-ČSL, ODA a KDS. " +
				"Koalice měla 105 poslanců. Druhou Klausovu vládu (4. července 1996 - 2. ledna 1998; " +
				"demise 30. listopadu 1997) pak tvořila koalice ODS, KDU-ČSL, ODA, která však měla jen 99 poslanců. " +
				"Z povolebních jednání si opoziční ČSSD odnesla křeslo předsedy Sněmovny pro Miloše Zemana výměnou za podporu vlády. " +
				"V premiérském křesle zůstal více než pět let, " +
				"až politická krize a odhalené podvody v hospodaření ODS jej donutily v prosinci 1997 odstoupit.";
		try {
			segmenter.execute();
		} catch (ExecutionException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
}
