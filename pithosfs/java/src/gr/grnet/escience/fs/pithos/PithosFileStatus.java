package gr.grnet.escience.fs.pithos;

import java.io.IOException;

import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.permission.FsPermission;

public class PithosFileStatus extends FileStatus {

	public PithosFileStatus() {
		// TODO Auto-generated constructor stub
	}

	public PithosFileStatus(FileStatus other) throws IOException {
		super(other);
		// TODO Auto-generated constructor stub
	}

	public PithosFileStatus(long length, boolean isdir, int block_replication,
			long blocksize, long modification_time, Path path) {
		super(length, isdir, block_replication, blocksize, modification_time,
				path);
		// TODO Auto-generated constructor stub
	}

	public PithosFileStatus(long length, boolean isdir, int block_replication,
			long blocksize, long modification_time, long access_time,
			FsPermission permission, String owner, String group, Path path) {
		super(length, isdir, block_replication, blocksize, modification_time,
				access_time, permission, owner, group, path);
		// TODO Auto-generated constructor stub
	}

	public PithosFileStatus(long length, boolean isdir, int block_replication,
			long blocksize, long modification_time, long access_time,
			FsPermission permission, String owner, String group, Path symlink,
			Path path) {
		super(length, isdir, block_replication, blocksize, modification_time,
				access_time, permission, owner, group, symlink, path);
		// TODO Auto-generated constructor stub
	}

}
