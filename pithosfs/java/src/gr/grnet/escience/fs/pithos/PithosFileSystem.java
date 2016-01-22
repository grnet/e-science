package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.commons.Utils;
import gr.grnet.escience.pithos.rest.HadoopPithosConnector;
import gr.grnet.escience.pithos.rest.PithosResponse;
import gr.grnet.escience.pithos.rest.PithosResponseFormat;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.FileInputStream;
import java.io.InputStream;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Properties;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.permission.FsPermission;
import org.apache.hadoop.util.Progressable;

/**
 * Implements a (partially) Hadoop Compatible File System using pithos+ as the
 * storage backend.
 *
 * @author eScience Dev Team
 * @version 0.1
 * @since March, 2015
 */
public class PithosFileSystem extends FileSystem {

    private URI uri;

    /** Interface to pithos+ REST API. */
    private static HadoopPithosConnector hadoopPithosConnector;

    private Path workingDir;

    /** holds string representation of a Path variable. */
    private String pathToString;

    private PithosPath pithosPath;

    private static String filename;

    private String[] filesList;

    private boolean isDir = false;

    private long length = 0;

    private PithosFileStatus pithosFileStatus;

    private PithosPath srcPiPath = null;

    private PithosPath dstPiPath = null;

    private String srcName = null;

    private String dstName = null;

    /** Holds HTTP response codes or strings. */
    private String response = null;

    private FSDataOutputStream fsDataOutputStreamInstance = null;

    /** Holds an urlsafe escaped string. */
    private String urlEsc;

    private PithosResponse metadata = null;

    /** Holds an escaped Path string. */
    private String pathEsc = null;

    private String modificationTime = null;

    private ArrayList<FileStatus> results = null;

    private FileStatus fileStatus = null;

    private String[] files = null;

    private FileStatus[] resultsArr = null;

    private PithosOutputStream pithosOutputStreamInstance = null;

    /** Default HDFS block size. */
    private static final long DEFAULT_HDFS_BLOCK_SIZE = (long) 128 * 1024 * 1024;

    /** Actual configured HDFS block size */
    private static long hdfsBlockSize = DEFAULT_HDFS_BLOCK_SIZE;

    /** mapreduce jobs input folder */
    private String fromAttemptDirectory = null;

    /** mapreduce jobs output root folder. */
    private String toOutputRootDirectory = null;

    private String[] resultFileName = null;

    private String copyFromFullPath = null;

    private String copyToFullPath = null;

    private FileStatus[] resultFilesList = null;

    private int resultFilesCounter = 0;

    /** Signifies mapreduce job end state. */
    private boolean commitCalled = false;

    private PithosPath commitPithosPath = null;
    
    private Properties kamaki_info = new Properties();

    /**
     * Instantiates a new pithos file system.
     */
    public PithosFileSystem() {
    }

    /**
     * Gets the hadoop pithos connector.
     *
     * @return the instance of hadoop - pithos connector
     */
    public static HadoopPithosConnector getHadoopPithosConnector() {
        return hadoopPithosConnector;
    }

    /**
     * Set the instance of hadoop - pithos connector.
     *
     * @param hadoopPithosConnectorIn
     *            the new hadoop pithos connector
     */
    public static void setHadoopPithosConnector(
            HadoopPithosConnector hadoopPithosConnectorIn) {
        PithosFileSystem.hadoopPithosConnector = hadoopPithosConnectorIn;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.apache.hadoop.fs.FileSystem#getScheme()
     */
    @Override
    public String getScheme() {
        return "pithos";
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.apache.hadoop.fs.FileSystem#getUri()
     */
    @Override
    public URI getUri() {
        return uri;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.apache.hadoop.fs.FileSystem#initialize(java.net.URI,
     * org.apache.hadoop.conf.Configuration)
     */
    @Override
    public void initialize(URI uri, Configuration conf) throws IOException {
        super.initialize(uri, conf);
        setConf(conf);
        if (conf.get("fs.pithos.debug") != null) {
            Boolean debug = Boolean.valueOf(conf.get("fs.pithos.debug"));
            Utils.setDebug(debug);
        }
    	try (InputStream kamakirc = new FileInputStream("/home/hduser/.kamakirc")) {	
    		kamaki_info.load(kamakirc);
    		kamakirc.close();
    	}
    	catch (IOException e) {
    		try (InputStream kamakirc = new FileInputStream(
					"/var/lib/hadoop-hdfs/.kamakirc")) {
				kamaki_info.load(kamakirc);
				kamakirc.close();
			} catch (IOException exc) {
				Utils.dbgPrint(
						"initialize > /home/hduser/.kamakirc error: ", e, 
						"  and initialize > /var/lib/hadoop-hdfs/.kamakirc error: ",
						exc);
			}
    	}        
        this.uri = URI.create(uri.getScheme() + "://" + uri.getAuthority());
        setWorkingDirectory(new Path("/user", System.getProperty("user.name")));
        hdfsBlockSize = conf.getLongBytes("dfs.blocksize",
                DEFAULT_HDFS_BLOCK_SIZE);
        if (hadoopPithosConnector == null) {
            setHadoopPithosConnector(new HadoopPithosConnector(
            		conf.get("fs.pithos.url"), kamaki_info.getProperty("token"),
                    kamaki_info.getProperty("uuid")));
        }

    }

    /*
     * (non-Javadoc)
     * 
     * @see org.apache.hadoop.fs.FileSystem#getWorkingDirectory()
     */
    @Override
    public Path getWorkingDirectory() {
        return workingDir;
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * org.apache.hadoop.fs.FileSystem#setWorkingDirectory(org.apache.hadoop
     * .fs.Path)
     */
    @Override
    public void setWorkingDirectory(Path dir) {
        workingDir = makeAbsolute(dir);
    }

    /**
     * Make absolute.
     *
     * @param path
     *            the path
     * @return the path
     */
    private Path makeAbsolute(Path path) {
        if (path.isAbsolute()) {
            return path;
        }
        return new Path(workingDir, path);
    }

    /**
     * This optional operation is not yet supported.
     *
     * @param f
     *            the f
     * @param bufferSize
     *            the buffer size
     * @param progress
     *            the progress
     * @return the FS data output stream
     * @throws IOException
     *             Signals that an I/O exception has occurred.
     */
    @Override
    public FSDataOutputStream append(Path f, int bufferSize,
            Progressable progress) throws IOException {
        throw new IOException("Not supported");
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.apache.hadoop.fs.FileSystem#create(org.apache.hadoop.fs.Path,
     * org.apache.hadoop.fs.permission.FsPermission, boolean, int, short, long,
     * org.apache.hadoop.util.Progressable)
     */
    @Override
    public FSDataOutputStream create(Path f, FsPermission permission,
            boolean overwrite, int bufferSize, short replication,
            long blockSize, Progressable progress) throws IOException {

        // - Initialize & release previously allocated memory
        pithosOutputStreamInstance = null;
        fsDataOutputStreamInstance = null;

        pithosPath = new PithosPath(f);

        // - Create empty object on Pithos FS with the given name by using the
        // path
        getHadoopPithosConnector().storePithosObject(pithosPath.getContainer(),
                new PithosObject(new PithosPath(f), null));

        pithosOutputStreamInstance = new PithosOutputStream(getConf(),
                pithosPath, getHadoopPithosConnector()
                        .getPithosBlockDefaultSize(pithosPath.getContainer()),
                1 * 1024 * 1024);

        fsDataOutputStreamInstance = new FSDataOutputStream(
                pithosOutputStreamInstance, statistics);

        return fsDataOutputStreamInstance;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.apache.hadoop.fs.FileSystem#delete(org.apache.hadoop.fs.Path,
     * boolean)
     */
    @Override
    public boolean delete(Path f, boolean recursive) throws IOException {
        Utils.dbgPrint("delete > path, recurse ", f, recursive);
        pithosPath = new PithosPath(f);
        response = getHadoopPithosConnector().deletePithosObject(
                pithosPath.getContainer(), pithosPath.getObjectAbsolutePath());
        if (response.contains("204")) {
            return true;
        }
        return false;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.apache.hadoop.fs.FileSystem#exists(org.apache.hadoop.fs.Path)
     */
    @Override
    public boolean exists(Path f) throws IOException {
        // keep for debug purposes
        return super.exists(f);
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * org.apache.hadoop.fs.FileSystem#getFileStatus(org.apache.hadoop.fs.Path)
     */
    @Override
    public PithosFileStatus getFileStatus(Path targetPath) throws IOException {

        // - Process the given path
        pithosPath = new PithosPath(targetPath);

        // - Check if it is the final call from outputstream and perform the
        // final action for the result file(s) movement
        if (PithosOutputStream.getStreamStatus() && !isCommitCalled()) {
            // - Set the current path as the one that constitutes the commit
            // directory for Hadoop outputstream
            setCommitPithosPath(pithosPath);

            // - Perform the final commit by moving the result files to the root
            // output folder
            commitFinalResult();
        }
        
        urlEsc = null;
        try {
            urlEsc = Utils.urlEscape(null, null,
                    pithosPath.getObjectAbsolutePath(), null);
        } catch (URISyntaxException e) {
            throw new IOException(e);
        }
        metadata = getHadoopPithosConnector().getPithosObjectMetaData(
                pithosPath.getContainer(), urlEsc, PithosResponseFormat.JSON);
        if (metadata.toString().contains("HTTP/1.1 404 NOT FOUND")) {
            throw new FileNotFoundException("File does not exist in Pithos FS.");
        }
        for (String obj : metadata.getResponseData().keySet()) {
            if (obj != null
                    && (obj.matches("Content-Type") || obj
                            .matches("Content_Type"))) {
                for (String fileType : metadata.getResponseData().get(obj)) {
                    if (fileType.contains("application/directory")
                            || fileType.contains("application/folder")) {
                        isDir = true;
                        break;
                    } else {
                        isDir = false;
                    }
                }
            }
        }
        if (isDir) {
            pithosFileStatus = new PithosFileStatus(true, hdfsBlockSize, false,
                    targetPath);
        } else {
            for (String obj : metadata.getResponseData().keySet()) {
                if (obj != null && obj.matches("Content-Length")) {
                    for (String lengthStr : metadata.getResponseData().get(obj)) {
                        length = Long.parseLong(lengthStr);
                    }
                }
            }
            modificationTime = metadata.getResponseData().get("Last-Modified")
                    .get(0);

            pithosFileStatus = new PithosFileStatus(length, hdfsBlockSize,
                    Utils.dateTimeToEpoch(modificationTime, ""), targetPath);
        }
        return pithosFileStatus;
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * org.apache.hadoop.fs.FileSystem#listStatus(org.apache.hadoop.fs.Path)
     */
    @Override
    public FileStatus[] listStatus(Path f) throws IOException {

        filename = "";
        pithosPath = new PithosPath(f);
        pathToString = pithosPath.toString();

        pathToString = pathToString.substring(this.getScheme().toString()
                .concat("://").length());

        filesList = pathToString.split("/");
        filename = filesList[filesList.length - 1];

        int count = 2;
        while (!filesList[filesList.length - count].equals(pithosPath
                .getContainer())) {
            filename = filesList[filesList.length - count] + "/" + filename;
            count++;
        }

        results = new ArrayList<FileStatus>();

        files = getHadoopPithosConnector().getFileList(
                pithosPath.getContainer()).split("\\r?\\n");

        // - Iterate on available files in the container
        for (int i = 0; i < files.length; i++) {
            String file = files[i].substring(files[i].lastIndexOf("/") + 1);
            files[i] = files[i].substring(0, files[i].length() - file.length());
            if ((filename + "/").equals(files[i])) {
                Path path = new Path("pithos://" + pithosPath.getContainer()
                        + "/" + filename + "/" + file);
                fileStatus = getFileStatus(path);
                results.add(fileStatus);
            }
        }
        // - Return the list of the available files
        resultsArr = new FileStatus[results.size()];

        return results.toArray(resultsArr);
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.apache.hadoop.fs.FileSystem#mkdirs(org.apache.hadoop.fs.Path,
     * org.apache.hadoop.fs.permission.FsPermission)
     */
    @Override
    public boolean mkdirs(Path f, FsPermission permission) throws IOException {
        pithosPath = new PithosPath(f);

        response = getHadoopPithosConnector().uploadFileToPithos(
                pithosPath.getContainer(),
                pithosPath.getObjectFolderAbsolutePath(), true);

        if (response != null && response.contains("201")) {
            return true;
        }

        return false;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.apache.hadoop.fs.FileSystem#open(org.apache.hadoop.fs.Path, int)
     */
    @Override
    public FSDataInputStream open(Path targetFile, int bufferSize)
            throws IOException {
        pithosPath = new PithosPath(targetFile);
        pathEsc = null;

        try {
            pathEsc = Utils.urlEscape(null, null,
                    pithosPath.getObjectAbsolutePath(), null);
        } catch (URISyntaxException e) {
            Utils.dbgPrint("open > invalid targetFile, error: ", e);
            throw new IOException(e);
        }

        return getHadoopPithosConnector().pithosObjectInputStream(
                pithosPath.getContainer(), pathEsc);
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.apache.hadoop.fs.FileSystem#rename(org.apache.hadoop.fs.Path,
     * org.apache.hadoop.fs.Path)
     */
    @Override
    public boolean rename(Path src, Path dst) throws IOException {

        srcPiPath = new PithosPath(src);
        dstPiPath = new PithosPath(dst);
        srcName = srcPiPath.getObjectAbsolutePath();
        dstName = dstPiPath.getObjectAbsolutePath();

        response = getHadoopPithosConnector().movePithosObjectToFolder(
                srcPiPath.getContainer(), srcName, "", dstName);

        if (response.contains("201")) {
            return true;
        } else {
            return false;
        }
    }

    /**
     * * Additional utility methods for finalizing result files to output
     * directory.
     * 
     * @return the commit pithos path
     */

    /**
     * 
     * @return: the full path of the temp files during the output-stream example
     */
    private PithosPath getCommitPithosPath() {
        return commitPithosPath;
    }

    /**
     * Sets the commit pithos path.
     *
     * @param _path
     *            the new commit pithos path
     */
    private void setCommitPithosPath(PithosPath _path) {
        this.commitPithosPath = _path;
    }

    /**
     * Checks if is commit called.
     *
     * @return true, if is commit called
     * @return: check if the commit method has been already called, in order to
     *          avoid any potential problems due to the recursive behavior of
     *          listStatus method
     */
    private boolean isCommitCalled() {
        return commitCalled;
    }

    /**
     * Perform the move of the final result files from the temp files to the
     * root output file, and delete the remaining unused temp files.
     */
    private void commitFinalResult() {

        // - Avoid the impact due to the recursive behavior
        this.commitCalled = true;

        // - Get the attempt folder of the output result
        fromAttemptDirectory = getCommitPithosPath().getObjectAbsolutePath();

        // - Get the root folder
        try
        {
        toOutputRootDirectory = getCommitPithosPath().getObjectAbsolutePath()
                .substring(
                        0,
                        getCommitPithosPath().getObjectAbsolutePath().indexOf(
                                "/_temporary"));
        
        }
        // - Catch the exception thrown when PithosPath used with commitFinalResult has no
        // _temporary folders. This happens due to a bug.
        catch (StringIndexOutOfBoundsException e)
        {
            this.commitCalled = false;
            return;
        }
             

        try {
            // - Get the file status by all available files into selected
            // results directory
            resultFilesList = listStatus(getCommitPithosPath()
                    .getPithosFSPath());

            // - Initialize the string array that includes the file names of the
            // result files
            resultFileName = new String[resultFilesList.length];

            // - Iterate on results directory contents
            resultFilesCounter = 0;

            // - Iterate on file status array results so as to get one-by-one
            // the available result file names
            for (FileStatus resultFileFStatus : resultFilesList) {
                // - Get the file name
                resultFileName[resultFilesCounter] = resultFileFStatus
                        .getPath().getName();

                // - increase the counter of the files
                resultFilesCounter++;
            }

        } catch (IOException e) {
            Utils.dbgPrint("commitFinalResult error: ", e);
        }

        // - Iterate on all results files
        for (String resultFile : resultFileName) {
            // - Create the full From --> To paths that will be used by PithosFS
            // methods so as to perform the move of the result files into pithos
            // file storage
            copyFromFullPath = fromAttemptDirectory.concat("/").concat(
                    resultFile);
            copyToFullPath = toOutputRootDirectory.concat("/").concat(
                    resultFile);

            // - Perform the move from the current temp directory to the root
            // output directory - on PithosFS
            PithosFileSystem.getHadoopPithosConnector()
                    .movePithosObjectToFolder("pithos", // container
                            copyFromFullPath, // source object
                            "", // folder path
                            copyToFullPath); // target object
        }

    }

    /**
     * Allows alternative packaging of dependencies into orka-pithos.jar.
     *
     * @param args
     */
    public static void main(String[] args) {
        // empty entry point method used to facilitate alternate packaging
    }

}
