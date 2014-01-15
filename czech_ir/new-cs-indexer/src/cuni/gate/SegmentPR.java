package cuni.gate;

import cuni.treex.Segmenter;

import java.io.IOException;

import gate.Resource;
import gate.creole.AbstractLanguageAnalyser;
import gate.creole.ExecutionException;
import gate.creole.ResourceInstantiationException;
import gate.creole.metadata.CreoleResource;
import gate.creole.metadata.CreoleParameter;

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
			defaultValue = "/home/mnovak/projects/khresmoi-mt/czech_ir/new-cs-indexer/tools/segment")
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
		
	}
	
}
