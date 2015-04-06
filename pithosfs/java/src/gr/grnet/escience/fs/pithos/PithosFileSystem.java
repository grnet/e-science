package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.pithos.rest.HadoopPithosConnector;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.URI;

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
 * Hadoop 2.6.0. Essentially the main idea here, respects to the development of
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

	private Path workingDir;

	private static HadoopPithosConnector hadoopPithosConnector;

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
		return getConf().getLong("fs.pithos.block.size", 4 * 1024 * 1024);
	}

	@Override
	public String getCanonicalServiceName() {
		System.out.println("getcanonicalservicename!");
		// Does not support Token
		return null;
	}

	@Override
	public FileStatus getFileStatus(Path arg0) throws IOException {
		System.out.println("here in getFileStatus BEFORE!");

		long pf_size = getHadoopPithosConnector().getPithosObjectSize("pithos",
				"server.txt");
		long pf_bsize = getHadoopPithosConnector().getPithosObjectBlockSize(
				"pithos", "server.txt");

		try {
			FileStatus pithos_file_status = new FileStatus(pf_size, false, 1,
					pf_bsize, 0, arg0);
			System.out.println("here in getFileStatus AFTER!");
			return pithos_file_status;
		} catch (Exception e) {
			System.out.println("URI exception thrown");
			return null;
		}
	}

	@Override
	public FileStatus[] listStatus(Path f) throws FileNotFoundException,
			IOException {
		System.out.println("list Status!");
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
	public boolean mkdirs(Path arg0, FsPermission arg1) throws IOException {
		System.out.println("Make dirs!");
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public FSDataInputStream open(Path arg0, int arg1) throws IOException {
		// TODO: parse the container
		return getHadoopPithosConnector().pithosObjectInputStream("pithos",
				"server.txt");
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
