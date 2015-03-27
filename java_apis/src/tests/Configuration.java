package tests;

import gr.grnet.escience.fs.pithos.PithosFileSystem;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.URISyntaxException;

import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.UnresolvedLinkException;
import org.apache.hadoop.security.AccessControlException;

public class Configuration {

	public static void main(String[] args) throws URISyntaxException, AccessControlException, FileNotFoundException, UnresolvedLinkException, IllegalArgumentException, IOException {
		PithosFileSystem pfs = new PithosFileSystem();
		pfs.configurations(new Path("pithosFile.txt"));
		
//		conf.set("fs.defaultFS", "hdfs://83.212.96.49");
//		conf.set("fs.AbstractFileSystem.pithos.impl", "gr.grnet.escience.fs.pithos.PithosAbstractFileSystem");
//		conf.set("hadoop.job.ugi", "hduser");
		
		//pafs.listStatus(new Path("/user/hduser"));	
		//FileStatus[] dis = pfs.listStatus(new Path("pithosFile.txt"));
	}
	
}
