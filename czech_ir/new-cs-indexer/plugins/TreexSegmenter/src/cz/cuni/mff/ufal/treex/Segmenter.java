package cz.cuni.mff.ufal.treex;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.ProcessBuilder;
import java.util.ArrayList;
import java.util.List;

public class Segmenter 
{
	public static final String DOCUMENT_END = "<__DOCUMENT_END__>";
	public static final String EXTERNAL_SPLIT = "<__EXTERNAL_SPLIT__>";
	
    ProcessBuilder pb = null;
    Process perlProcess = null;
    
    public Segmenter(String workingDir) throws IOException {
        this.pb = new ProcessBuilder("./segment.pl");
        this.pb.directory(new File(workingDir));
        this.pb.redirectErrorStream();
        this.perlProcess = this.pb.start();
    }
    
    public List<String> process_text(String text) throws IOException {
    	return process_text(text, false);
    }
    
    public List<String> process_text(String text, boolean withExternalSplits) throws IOException {
    	StringBuilder sb = new StringBuilder(text);
    	sb.append("\n").append(DOCUMENT_END).append("\n");
    	text = sb.toString();
    	this.perlProcess.getOutputStream().write(text.getBytes());
    	this.perlProcess.getOutputStream().flush();
    	
    	List<String> sentences = new ArrayList<String>();
    	
    	BufferedReader perlInputReader = 
    			new BufferedReader(new InputStreamReader(this.perlProcess.getInputStream()));
    	String line = null;
    	while ((line = perlInputReader.readLine()) != null && !line.equals(DOCUMENT_END))
    		sentences.add(line);
    	
    	return sentences;
    }

    
    public static void main(String[] args) {
    	String workingDir = "./scripts"; 
    	try {
	    	Segmenter bipipe = new Segmenter(workingDir);
	    	
	    	BufferedReader inputReader = 
	    			new BufferedReader(new InputStreamReader(System.in));
	    	String line = null;
	    	while ((line = inputReader.readLine()) != null)
	    	{
	    		List<String> sentences = bipipe.process_text(line);
	    		for (int i = 0; i < sentences.size(); i++)
	    		{
	    			System.out.println(sentences.get(i));
	    		}
	    	}
    	}
    	catch (IOException e) {
    		System.err.println("IO Problem: " + e.getMessage());
    	}
    }
}
