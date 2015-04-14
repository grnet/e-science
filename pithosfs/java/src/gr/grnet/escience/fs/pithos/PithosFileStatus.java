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

	/**
	 * Compare if this object is equal to another object
	 * 
	 * @param o
	 *            the object to be compared.
	 * @return true if two file status has the same path name; false if not.
	 */
	@Override
	public boolean equals(Object o) {
		return super.equals(o);
	}

	/**
	 * Returns a hash code value for the object, which is defined as the hash
	 * code of the path name.
	 * 
	 * @return a hash code value for the path name.
	 */
	@Override
	public int hashCode() {
		return super.hashCode();
	}
}
