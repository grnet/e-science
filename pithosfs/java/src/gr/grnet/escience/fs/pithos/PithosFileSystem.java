package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.pithos.rest.HadoopPithosConnector;
import gr.grnet.escience.pithos.rest.PithosResponse;
import gr.grnet.escience.pithos.rest.PithosResponseFormat;

import java.io.IOException;
import java.net.URI;
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
	// private String container;
	// private String objectPathStr;
	// private String fsPathStr;
	private PithosPath pithosPath;

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
		//this.workingDir = new Path("/user", System.getProperty("user.name"))
				//.makeQualified(this.uri, this.getWorkingDirectory());
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
		//pithosPath = new PithosPath(new Path(getUri().toString()));
		//return getHadoopPithosConnector().getPithosBlockDefaultSize("");
		return 128 * 1024 * 1024;
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

	@Override
	public PithosFileStatus getFileStatus(Path targetPath) throws IOException {

		System.out.println("here in getFileStatus BEFORE!");
		System.out.println("Path: " + targetPath.toString());
		// - Process the given path
		pithosPath = new PithosPath(targetPath);

		PithosResponse metadata = getHadoopPithosConnector()
				.getPithosObjectMetaData(pithosPath.getContainer(),
						pithosPath.getObjectPath(), PithosResponseFormat.JSON);

		if (metadata.toString().contains("404")) {
			System.out.println("File does not exist in Pithos FS.");
			exist = false;
		}

		if (exist) {
			for (String obj : metadata.getResponseData().keySet()) {
				if (obj != null) {
					if (obj.matches("Content-Type")) {
						for (String fileType : metadata.getResponseData().get(
								obj)) {
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
				pithos_file_status = new PithosFileStatus(true, getDefaultBlockSize(), false,
						targetPath); // arg0.makeQualified(this.uri,
				// this.workingDir));
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
				pithos_file_status = new PithosFileStatus(length, getDefaultBlockSize(), 123,
						targetPath);
			}
		}

		System.out.println("here in getFileStatus AFTER!");
		return pithos_file_status;
	}

	@Override
	public FileStatus[] listStatus(Path f) {
		System.out.println("\n--->  List Status Method!");

		pithosPath = new PithosPath(f);
		pathToString = pithosPath.toString();

		pathToString = pathToString.substring(this.getScheme().toString()
				.concat("://").length());

		filesList = pathToString.split("/");

		String conList = getHadoopPithosConnector().getFileList(
				pithosPath.getContainer());
		String targetFolder = filesList[filesList.length - 1];

		final List<FileStatus> result = new ArrayList<FileStatus>();
		FileStatus fileStatus;
		String files[] = conList.split("\\r?\\n");

		// - Iterate on available files in the container
		for (int i = 0; i < files.length; i++) {
			if (files[i].contains(targetFolder + "/")) {
				Path path = new Path(this.getScheme() + "://"
						+ pithosPath.getContainer() + "/" + files[i]);
				try {
					fileStatus = getFileStatus(path);
					System.out.println(files[i]);
					result.add(fileStatus);
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}// end for

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
		return getHadoopPithosConnector().pithosObjectInputStream(pithosPath.getContainer(),
				pithosPath.getObjectPath());
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
		System.out.println("Pithos FileSystem Connector loaded.");
	}

}
