package gr.grnet.escience.fs.pithos;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.URI;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.AbstractFileSystem;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.UnresolvedLinkException;
import org.apache.hadoop.fs.permission.FsPermission;
import org.apache.hadoop.security.AccessControlException;
import org.apache.hadoop.util.Progressable;
import org.orka.hadoop.pithos.rest.HadoopPithosRestConnector;


/**
 * This class implements a custom file system based on FIleSystem class of Hadoop 2.6.0.
 * Essentially the main idea here, respects to the development of a custom File System 
 * that will be able to allow the interaction between hadoop and pithos storage system.
 * 
 * @since March, 2015
 * @author Dimitris G. Kelaidonis (kelaidonis@gmail.com)
 * @version 0.1
 * 
 */
public class PithosFileSystem extends FileSystem {

	private URI uri;
    private HadoopPithosRestConnector p_connector;
	private Path workingDir;

	public PithosFileSystem() {
		// Initialize it by implementing the interface PithosSystemStore
	}
	
	public void configurations(Path f) throws IOException {
		Configuration conf = new Configuration();
		conf.get("fs.defaultFS");
		FileSystem fs = FileSystem.get(conf);
		System.out.println("fs.defaultFS --> : " + conf.get("fs.defaultFS"));
		System.out.println("fs.pithos.access.key --> : " + conf.get("fs.pithos.access.key"));
		System.out.println("fs.pithos.secret.key --> : " + conf.get("fs.pithos.secret.key"));
		System.out.println("fs.pithos.impl --> : " + conf.get("fs.pithos.impl"));
		System.out.println("fs.pithos.url --> : " + conf.get("fs.pithos.url"));
		System.out.println("fs.default.name --> : " + conf.get("fs.default.name"));
		HadoopPithosRestConnector conn = new HadoopPithosRestConnector(conf.get("fs.pithos.url"), conf.get("fs.pithos.secret.key"), conf.get("fs.pithos.access.key"));
		String container = f.getParent().toString();
		conn.getPithosObject(container, f.toString(), "/home/hduser");
	}

	@Override
	public String getScheme() {
		System.out.println("here in getScheme");
		return "pithos";
	}

	@Override
	public URI getUri() {
		System.out.println("here in getUri");
		return uri;
	}

	@Override
	public void initialize(URI uri, Configuration conf) throws IOException {
		super.initialize(uri, conf);
		this.p_connector = new HadoopPithosRestConnector(conf.get("fs.pithos.url"), conf.get("auth.pithos.token"), conf.get("auth.pithos.uuid"));
		System.out.println(uri.toString());
        System.out.println(conf.toString());
        System.out.println(conf.get("fs.pithos.impl"));
		this.setConf(conf);
		System.out.println(conf.getClassByNameOrNull(conf.get("fs.pithos.impl")));
		System.out.println("here in initialize");
		this.uri = uri; //URI.create(uri.getScheme() + "://" + uri.getAuthority());
		this.workingDir = new Path("/user", System.getProperty("user.name"));
		System.out.println(this.uri.getScheme());
		System.out.println(this.uri.toString());
		//System.out.println(this.uri.toURL());
		System.out.println(this.workingDir.toString());
	}

	@Override
	public Path getWorkingDirectory() {
		System.out.println("here in getWorkingDirectory");
		return workingDir;
	}

	@Override
	public void setWorkingDirectory(Path dir) {
		System.out.println("here in setWorkingDir");
		workingDir = makeAbsolute(dir);
	}

	private Path makeAbsolute(Path path) {
		System.out.println("here in makeabsolute path");
		if (path.isAbsolute()) {
			return path;
		}
		return new Path(workingDir, path);
	}

	/** This optional operation is not yet supported. */
	@Override
	public FSDataOutputStream append(Path f, int bufferSize,
			Progressable progress) throws IOException {
		throw new IOException("data output stream Not supported");
	}


	@Override
	public long getDefaultBlockSize() {
		System.out.println("in getdefaultBlockSize");
		return getConf().getLong("fs.pithos.block.size", 4 * 1024 * 1024);
	}

	@Override
	public String getCanonicalServiceName() {
		// Does not support Token
		
		System.out.println("here in getcanonical");
		return null;
	}

	@Override
	public FSDataOutputStream create(Path arg0, FsPermission arg1,
			boolean arg2, int arg3, short arg4, long arg5, Progressable arg6)
			throws IOException {
		// TODO Auto-generated method stub
		System.out.println("here in data output stream");
		return null;
	}

	@Override
	public boolean delete(Path arg0, boolean arg1) throws IOException {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public FileStatus getFileStatus(Path arg0) throws IOException {
		// TODO Auto-generated method stub
		// First method that needs implementing, probably FileStatus class also.
		System.out.println(arg0.toString());
		System.out.println(this.p_connector.readPithosObject("", "mock/mock-1.0.1.pdf").available());
		return null;
		//FileStatus pithos_file_status = new FileStatus(363448, false,0, this.getDefaultBlockSize(),0,
				//0, null, null, null, arg0);
		//System.out.println("here in getFileStatus");
		//return pithos_file_status;
	}

	@Override
	public FileStatus[] listStatus(Path f) throws FileNotFoundException,
			IOException {
		FileStatus fstat = this.getFileStatus(f);
		Configuration conf = new Configuration();
//		conf.get("fs.defaultFS");
//		conf.get("fs.orka.default.config.path");
//		conf.get("fs.pithos.impl");
		//conf.addResource(new Path("/home/developer/core-site.xml"));
		//conf.set("fs.defaultFS", "hdfs://83.212.96.14:9000");
		conf.get("fs.defaultFS");
//		conf.set("fs.defaultFS", "hdfs://83.212.96.14:9000");
//		conf.set("fs.pithos.impl", "gr.grnet.escience.fs.pithos.PithosFileSystem");
		//- Add Serial Port parameters
		//conf.set("hadoop.job.ugi", "hduser");
//		HadoopPithosRestConnector conn = new HadoopPithosRestConnector();
//		String container = f.getParent().toString();
//		FSDataInputStream fsdis = conn.readPithosObject(container, f.toString());
		FileSystem fs = FileSystem.get(conf);
		//HadoopPithosRestConnector conn = new HadoopPithosRestConnector();
		String container = f.getParent().toString();
		//File pithosActualObject = conn.getPithosObject(container, f.toString(), "/user/hduser");
		//System.out.println("File name: " + pithosActualObject.getName());
//		FileStatus[] status = fs.listStatus(f);
//        for(int i=0;i<status.length;i++){
//            System.out.println(status[i].getPath());
//            System.out.println(conf.get("fs.defaultFS"));
//        }
		System.out.println("here in liststatus");
		return null;
		// TODO Auto-generated method stub
	}

	@Override
	public boolean mkdirs(Path arg0, FsPermission arg1) throws IOException {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public FSDataInputStream open(Path arg0, int arg1) throws AccessControlException, FileNotFoundException,
	UnresolvedLinkException, IOException {
		// TODO: Get data from Pithos by using Hadoop Pithos Connector		
		System.out.println("here in fsdatainputstream");	
	    //FSDataInputStream fsdis = this.open(arg0);
	    
	//HadoopPithosRestConnector conn = new HadoopPithosRestConnector();
	    String container = arg0.getParent().toString();
	    System.out.println(container);
	//FSDataInputStream fsdis = conn.readPithosObject(container, path.toString()); 
	//FSDataInputStream ffsdis = new FSDataInputStream(fsdis);
	// TODO
	    return null;
	}

	@Override
	public boolean rename(Path arg0, Path arg1) throws IOException {
		// TODO Auto-generated method stub
		return false;
	}
	
    public static void main(String s[]){
    	
    	System.out.println("am i here???");
    	
    }
}
