package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.commons.Utils;
import gr.grnet.escience.pithos.rest.HadoopPithosConnector;
import gr.grnet.escience.pithos.rest.PithosResponse;
import gr.grnet.escience.pithos.rest.PithosResponseFormat;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.permission.FsPermission;
import org.apache.hadoop.util.Progressable;

/**
 * This class implements a custom file system based on FIleSystem class of
 * Hadoop 2.5.2. Essentially the main idea here, respects to the development of
 * a custom File System that will be able to allow the interaction between
 * hadoop and pithos storage system.
 * 
 * @since March, 2015
 * @author Dimitris G. Kelaidonis & Ioannis Stenos
 * @version 0.1
 * 
 */
public class PithosFileSystem extends FileSystem {

	private URI uri;
	private static HadoopPithosConnector hadoopPithosConnector;
	private Path workingDir;
	private String pathToString;
	private PithosPath pithosPath;
	static String filename;

	private String[] filesList;
	private boolean exist = true;
	private boolean isDir = false;
	private long length = 0;
	private PithosFileStatus pithos_file_status;
	public static final Log LOG = LogFactory.getLog(PithosFileSystem.class);

	public PithosFileSystem() {
	}

	public String getConfig(String param) {
		Configuration conf = new Configuration();
		String result = conf.get(param);
		return result;
	}

	/**
	 * @return the instance of hadoop - pithos connector
	 */
	public static HadoopPithosConnector getHadoopPithosConnector() {
		return hadoopPithosConnector;
	}

	/**
	 * Set thes instance of hadoop - pithos connector
	 */
	public static void setHadoopPithosConnector(
			HadoopPithosConnector hadoopPithosConnector) {
		PithosFileSystem.hadoopPithosConnector = hadoopPithosConnector;
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
		System.out.println(this.uri.toString());
		this.workingDir = new Path("/user", System.getProperty("user.name"));
		// this.workingDir = new Path("/user", System.getProperty("user.name"))
		// .makeQualified(this.uri, this.getWorkingDirectory());
		System.out.println(this.workingDir.toString());
		System.out.println("Create System Store connector");

		// - Create instance of Hadoop connector
		setHadoopPithosConnector(new HadoopPithosConnector(
				getConfig("fs.pithos.url"), getConfig("auth.pithos.token"),
				getConfig("auth.pithos.uuid")));

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
		return getConf().getLong("dfs.blocksize", 4 * 1024 * 1024);
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
		System.out.println("Create!");
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public boolean delete(Path arg0, boolean arg1) throws IOException {
		System.out.println("Delete!");
		// TODO Auto-generated method stub
		return false;
	}
	
	public boolean ContainerExistance(String container) {
		PithosResponse containerInfo = getHadoopPithosConnector()
				.getContainerInfo(container);
		if (containerInfo.toString().contains("404")) {
			return false;
		} else {
			return true;
		}
	}

	@Override
	public PithosFileStatus getFileStatus(Path targetPath) throws IOException {
		System.out.println("here in getFileStatus BEFORE!");
		System.out.println("Path: " + targetPath.toString());
		// - Process the given path
		pithosPath = new PithosPath(targetPath);

		PithosResponse metadata = getHadoopPithosConnector()
				.getPithosObjectMetaData(pithosPath.getContainer(),
						pithosPath.getObjectAbsolutePath(), PithosResponseFormat.JSON);

		if (metadata.toString().contains("404")) {
			FileNotFoundException fnfe = new FileNotFoundException("File does not exist in Pithos FS.");
			throw fnfe;
		}		
		for (String obj : metadata.getResponseData().keySet()) {
			if (obj != null) {
				if (obj.matches("Content-Type") || obj.matches("Content_Type")) {
					for (String fileType : metadata.getResponseData()
							.get(obj)) {
						if (fileType.contains("application/directory")) {
							isDir = true;
							break;
						} else {
							isDir = false;
						}
					}
				}
			}
		}
		if (isDir) {
			pithos_file_status = new PithosFileStatus(true, getDefaultBlockSize(), false, targetPath); 
		} else {				
			for (String obj : metadata.getResponseData().keySet()) {
				if (obj != null) {
					if (obj.matches("Content-Length")) {
						for (String lengthStr : metadata.getResponseData()
								.get(obj)) {
							length = Long.parseLong(lengthStr);
						}
					}
				}
			}
			pithos_file_status = new PithosFileStatus(length, getDefaultBlockSize(), 123, targetPath);
		}
		System.out.println("here in getFileStatus AFTER!");
		return pithos_file_status;
	}

	@Override
	public FileStatus[] listStatus(Path f) throws FileNotFoundException,
			IOException {
		System.out.println("\n--->  List Status Method!");

		filename = "";
 		pithosPath = new PithosPath(f);
		pathToString = pithosPath.toString();

		pathToString = pathToString.substring(this.getScheme().toString()
				.concat("://").length());

		filesList = pathToString.split("/");
		filename = filesList[filesList.length - 1];
		int count = 2;
		while (!filesList[filesList.length-count].equals(pithosPath.getContainer())){
			filename = filesList[filesList.length-count]+"/"+filename;
			count ++;
		}
		
		final List<FileStatus> result = new ArrayList<FileStatus>();
		FileStatus fileStatus; 
		
		String files[] = getHadoopPithosConnector().getFileList(pithosPath.getContainer()).split("\\r?\\n");
		// - Iterate on available files in the container
		for (int i = 0; i < files.length; i++) {
			String file = files[i].substring(files[i].lastIndexOf("/")+1);
			files[i] = files[i].substring(0, (files[i].length() - file.length()));
			if ((filename + "/").equals(files[i])) {
				Path path = new Path("pithos://"+pithosPath.getContainer()+"/"+filename + "/" + file);
				fileStatus = getFileStatus(path);
				result.add(fileStatus);
			}
		}
		
		// - Return the list of the available files
		if (!result.isEmpty()) {
			return result.toArray(new FileStatus[result.size()]);
		} else {
			return null;
		}
	}

	@Override
	public boolean mkdirs(Path arg0, FsPermission arg1) throws IOException {
		System.out.println("Make dirs!");
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public FSDataInputStream open(Path target_file, int buffer_size)
			throws IOException {
		// TODO: parse the container
		pithosPath = new PithosPath(target_file);
		return getHadoopPithosConnector().pithosObjectInputStream(
				pithosPath.getContainer(), pithosPath.getObjectAbsolutePath());
	}

	@Override
	public boolean rename(Path arg0, Path arg1) throws IOException {
		System.out.println("rename!");
		// TODO Auto-generated method stub
		return false;
	}

	/**
	 * 
	 * @param args
	 */
	public static void main(String[] args) {
		// Stub so we can create a 'runnable jar' export for packing
		// dependencies
		Utils util = new Utils();
		String out = null;
		try {
			out = util.computeHash("Lorem ipsum dolor sit amet.", "SHA-256");
		} catch (NoSuchAlgorithmException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (UnsupportedEncodingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		System.out.println("Pithos FileSystem Connector loaded.");
		System.out.println("Test hashing: " + out);
	}

}
