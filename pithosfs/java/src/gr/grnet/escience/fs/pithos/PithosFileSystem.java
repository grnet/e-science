package gr.grnet.escience.fs.pithos;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.UnresolvedLinkException;
import org.apache.hadoop.fs.permission.FsPermission;
import org.apache.hadoop.security.AccessControlException;
import org.apache.hadoop.util.Progressable;
import org.codehaus.jettison.json.JSONException;
import org.codehaus.jettison.json.JSONObject;

import gr.grnet.escience.pithos.rest.HadoopPithosRestConnector;
import gr.grnet.escience.pithos.rest.PithosResponse;
import gr.grnet.escience.pithos.rest.PithosResponseFormat;


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

	private Path workingDir;
	public static final Log LOG = LogFactory.getLog(PithosFileSystem.class);

	public PithosFileSystem() {
		// Initialize it by implementing the interface PithosSystemStore
	}
	
	public String getConfig(String param){
		Configuration conf = new Configuration();
		String result = conf.get(param);
		return result;
	}

	@Override
	public String getScheme() {
		System.out.println("getScheme!");
		return "pithos";
	}

	@Override
	public URI getUri() {
		System.out.println("GetUri!");
		return uri;
	}

	@Override
	public void initialize(URI uri, Configuration conf) throws IOException {
		super.initialize(uri, conf);
		System.out.println("Initialize!");
		setConf(conf);
		this.uri = URI.create(uri.getScheme() + "://" + uri.getAuthority());
		workingDir = new Path("/user", System.getProperty("user.name")).makeQualified(this.uri,
				this.getWorkingDirectory());
		//this.workingDir = new Path("/user", System.getProperty("user.name"));
	}

	@Override
	public Path getWorkingDirectory() {
		System.out.println("getWorkingDirectory!");
		return workingDir;
	}

	@Override
	public void setWorkingDirectory(Path dir) {
		System.out.println("SetWorkingDirectory!");
		workingDir = makeAbsolute(dir);
	}

	private Path makeAbsolute(Path path) {
		if (path.isAbsolute()) {
			return path;
		}
		return new Path(workingDir, path);
	}

	/** This optional operation is not yet supported. */
	@Override
	public FSDataOutputStream append(Path f, int bufferSize,
			Progressable progress) throws IOException {
		System.out.println("append!");
		throw new IOException("Not supported");
	}


	@Override
	public long getDefaultBlockSize() {
		System.out.println("blockSize!");
		return getConf().getLong("fs.pithos.block.size", 4 * 1024 * 1024);
	}

	@Override
	public String getCanonicalServiceName() {
		System.out.println("getcanonicalservicename!");
		// Does not support Token
		return null;
	}

	@Override
	public FSDataOutputStream create(Path arg0, FsPermission arg1,
			boolean arg2, int arg3, short arg4, long arg5, Progressable arg6)
			throws IOException {
		System.out.println("create!");
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public boolean delete(Path arg0, boolean arg1) throws IOException {
		System.out.println("deelete!");
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public PithosFileStatus getFileStatus(Path arg0) throws IOException {
		boolean exist = false;
		long length = 0;
		PithosFileStatus pithos_file_status = null;
		System.out.println("here in getFileStatus BEFORE!");
		System.out.println(arg0.toString());
//		long length = conn.getPithosObjectBlockSize("pithos", arg0.toString());
//		System.out.println("length: " + length);
//		FileStatus pithos_file_status = new FileStatus(12345, false,0, this.getDefaultBlockSize(),0,
//				0, null, null, null, arg0);
//		int x = conn.readPithosObject("", "pithosFile.txt").available();
//		System.out.println(x);
//		System.out.println("X = " + x);
		HadoopPithosRestConnector conn = new HadoopPithosRestConnector(getConfig("fs.pithos.url"), getConfig("auth.pithos.token"), getConfig("auth.pithos.uuid"));
		/*---Check if file exist in pithos------------------------------------*/
		String container = arg0.getParent().toString();
		container = container.substring(container.lastIndexOf(container) + 9);
		System.out.println("Container: " + container);
		String conList = conn.getContainerList(container);
		System.out.println("Container List: \n" + conList);
		String filename = arg0.toString().substring(arg0.toString().lastIndexOf('/') + 1,
				arg0.toString().length());
		System.out.println(filename);
		if (conList.contains(filename)){
//			System.out.println("exists");
			exist = true;
		}else{
			System.out.println("File does not exist in Pithos FS.");
			return null;
		}		
		/*---------------------------------------------------------*/
		if (exist){
			PithosResponse metadata = conn.getPithosObjectMetaData(container, filename, PithosResponseFormat.JSON);
			try {
				System.out.println("metadata: " + metadata.toString());
				JSONObject obj = new JSONObject(metadata.toString());
				String contentLength = obj.getJSONObject("pithosResponse").getString("Content-Length");
				int left = contentLength.indexOf("[\"");
				int right = contentLength.indexOf("\"]");
				String objlength = contentLength.substring(left+2, right);
				length = Long.parseLong(objlength);
				System.out.println(length);
				pithos_file_status = new PithosFileStatus(length, 1265140799, arg0);
			} catch (JSONException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}				
		System.out.println("here in getFileStatus AFTER!");
		return pithos_file_status;
	}

	@Override
	public FileStatus[] listStatus(Path f) throws FileNotFoundException,
			IOException {
		System.out.println("list Status!");		
		//- Add Serial Port parameters
		//conf.set("hadoop.job.ugi", "hduser");
//		HadoopPithosRestConnector conn = new HadoopPithosRestConnector();
//		String container = f.getParent().toString();
//		FSDataInputStream fsdis = conn.readPithosObject(container, f.toString());
//		FileSystem fs = FileSystem.get(conf);
		//HadoopPithosRestConnector conn = new HadoopPithosRestConnector();
//		String container = f.getParent().toString();
		//File pithosActualObject = conn.getPithosObject(container, f.toString(), "/user/hduser");
		//System.out.println("File name: " + pithosActualObject.getName());
//		FileStatus[] status = fs.listStatus(f);
//        for(int i=0;i<status.length;i++){
//            System.out.println(status[i].getPath());
//            System.out.println(conf.get("fs.defaultFS"));
//        }
        return null;
		// TODO Auto-generated method stub
	}

	@Override
	public boolean mkdirs(Path arg0, FsPermission arg1) throws IOException {
		System.out.println("Make dirs!");
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public FSDataInputStream open(Path arg0, int arg1) throws IOException {
		System.out.println("Open!");
		// TODO: Get data from Pithos by using Hadoop Pithos Connector
		return null;
	}

	@Override
	public boolean rename(Path arg0, Path arg1) throws IOException {
		System.out.println("rename!");
		// TODO Auto-generated method stub
		return false;
	}
	
	public static void main(String[] args) {
		// Stub so we can create a 'runnable jar' export for packing depencencies
		System.out.println("Pithos FileSystem Connector loaded.");
	}
	
}
