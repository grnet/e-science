package gr.grnet.escience.fs.pithos;

import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;

public class PithosFileStatus extends FileStatus {

	private boolean isEmptyDirectory;

	// Directories
	public PithosFileStatus(boolean isdir, long blockSize, boolean isemptydir, Path path) {
		super(0, isdir, 1, blockSize, 0, path);
		isEmptyDirectory = isemptydir;
	}

	// Files
	public PithosFileStatus(long length, long blockSize, long modification_time, Path path) {
		super(length, false, 1, blockSize, modification_time, path);
		isEmptyDirectory = false;
	}

	public boolean isEmptyDirectory() {
		return isEmptyDirectory;
	}
}
