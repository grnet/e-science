package gr.grnet.escience.fs.pithos;

import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;

/**
 * Stores pithos+ file status information structure.
 * 
 */
public class PithosFileStatus extends FileStatus {

    private boolean isEmptyDirectory;

    /**
     * Instantiates a new pithos file status.
     *
     * @param isdir
     *            : is a directory object - boolean
     * @param blockSize
     *            : object container block size
     * @param isemptydir
     *            : isdir and empty
     * @param path
     *            : the path
     */
    // Directories
    public PithosFileStatus(boolean isdir, long blockSize, boolean isemptydir,
            Path path) {
        super(0, isdir, 1, blockSize, 0, path);
        isEmptyDirectory = isemptydir;
    }

    /**
     * Instantiates a new pithos file status.
     *
     * @param length
     *            the length
     * @param blockSize
     *            the block size
     * @param modificationTime
     *            the modification time
     * @param path
     *            the path
     */
    // Files
    public PithosFileStatus(long length, long blockSize, long modificationTime,
            Path path) {
        super(length, false, 1, blockSize, modificationTime, path);
        isEmptyDirectory = false;
    }

    /**
     * Checks if is empty directory.
     *
     * @return true, if is empty directory
     */
    public boolean isEmptyDirectory() {
        return isEmptyDirectory;
    }
}
