package tests;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.URISyntaxException;

import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.UnresolvedLinkException;
import org.apache.hadoop.security.AccessControlException;
import gr.grnet.escience.fs.pithos.PithosFileSystem;

public class Test {

	/**
	 * @param args
	 * @throws URISyntaxException 
	 * @throws IOException 
	 * @throws IllegalArgumentException 
	 * @throws UnresolvedLinkException 
	 * @throws FileNotFoundException 
	 * @throws AccessControlException 
	 */
//	public static void main(String[] args) throws URISyntaxException, AccessControlException, FileNotFoundException, UnresolvedLinkException, IllegalArgumentException, IOException {
//		PithosAbstractFileSystem pafs = new PithosAbstractFileSystem(new URI("hdfs://83.212.96.14"), "hdfs", false, 7000);
//		
//		//pafs.listStatus(new Path("/user"));	
//		FSDataInputStream dis = pafs.open(new Path("file.txt"), 512);
//	}
	
	public static void main(String[] args) throws URISyntaxException, AccessControlException, FileNotFoundException, UnresolvedLinkException, IllegalArgumentException, IOException {
		PithosFileSystem pfs = new PithosFileSystem();
//		Configuration conf = new Configuration();
//		conf.set("fs.defaultFS", "hdfs://83.212.96.49");
//		conf.set("fs.AbstractFileSystem.pithos.impl", "gr.grnet.escience.fs.pithos.PithosAbstractFileSystem");
//		conf.set("hadoop.job.ugi", "hduser");
		
		//pafs.listStatus(new Path("/user/hduser"));	
		FileStatus[] dis = pfs.listStatus(new Path("pithosFile.txt"));
	}

}