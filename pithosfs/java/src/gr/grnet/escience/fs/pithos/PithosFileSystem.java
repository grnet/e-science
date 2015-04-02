package gr.grnet.escience.fs.pithos;

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

	public PithosFileSystem() {
		// Initialize it by implementing the interface PithosSystemStore
	}

	@Override
	public String getScheme() {
		return "pithos";
	}

	@Override
	public URI getUri() {
		return uri;
	}

	@Override
	public void initialize(URI uri, Configuration conf) throws IOException {
		super.initialize(uri, conf);

		setConf(conf);
		this.uri = URI.create(uri.getScheme() + "://" + uri.getAuthority());
		this.workingDir = new Path("/user", System.getProperty("user.name"));
	}

	@Override
	public Path getWorkingDirectory() {
		return workingDir;
	}

	@Override
	public void setWorkingDirectory(Path dir) {
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
		throw new IOException("Not supported");
	}


	@Override
	public long getDefaultBlockSize() {
		return getConf().getLong("fs.pithos.block.size", 4 * 1024 * 1024);
	}

	@Override
	public String getCanonicalServiceName() {
		// Does not support Token
		return null;
	}

	@Override
	public FSDataOutputStream create(Path arg0, FsPermission arg1,
			boolean arg2, int arg3, short arg4, long arg5, Progressable arg6)
			throws IOException {
		// TODO Auto-generated method stub
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
		return null;
	}

	@Override
	public FileStatus[] listStatus(Path arg0) throws FileNotFoundException,
			IOException {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public boolean mkdirs(Path arg0, FsPermission arg1) throws IOException {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public FSDataInputStream open(Path arg0, int arg1) throws IOException {
		// TODO: Get data from Pithos by using Hadoop Pithos Connector
		return null;
	}

	@Override
	public boolean rename(Path arg0, Path arg1) throws IOException {
		// TODO Auto-generated method stub
		return false;
	}
	
	public static void main(String[] args) {
		// Stub so we can create a 'runnable jar' export for packing dependencies
		System.out.println("Pithos FileSystem Connector loaded.");
	}	
	
}
