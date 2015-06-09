package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.commons.Utils;
import gr.grnet.escience.pithos.rest.HadoopPithosConnector;
import gr.grnet.escience.pithos.rest.PithosResponse;
import gr.grnet.escience.pithos.rest.PithosResponseFormat;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.net.URISyntaxException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;

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
 * @author eScience Dev Team
 * @version 0.1
 * 
 */
public class PithosFileSystem extends FileSystem {

    private URI uri;
    private static HadoopPithosConnector hadoopPithosConnector;
    private Path workingDir;
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
    private String resp = null;
    private FSDataOutputStream fsDataOutputStreamInstance = null;
    private String urlEsc;
    private PithosResponse metadata = null;
    private String pathEsc = null;
    private String modificationTime = null;
    private ArrayList<FileStatus> results = null;
    private FileStatus fileStatus = null;
    private String[] files = null;
    private FileStatus[] resultsArr = null;
    private PithosOutputStream pithosOutputStreamInstance = null;
    private final long DEFAULT_HDFS_BLOCK_SIZE = 128 * 1024 * 1024;

    public PithosFileSystem() {
    }

    /**
     * @return the instance of hadoop - pithos connector
     */
    public static HadoopPithosConnector getHadoopPithosConnector() {
        return hadoopPithosConnector;
    }

    /**
     * Set the instance of hadoop - pithos connector
     */
    public static void setHadoopPithosConnector(
            HadoopPithosConnector hadoopPithosConnectorIn) {
        PithosFileSystem.hadoopPithosConnector = hadoopPithosConnectorIn;
    }

    @Override
    public String getScheme() {
        Utils.dbgPrint("getScheme >", "pithos");
        return "pithos";
    }

    @Override
    public URI getUri() {
        Utils.dbgPrint("getUri >", uri);
        return uri;
    }

    @Override
    public void initialize(URI uri, Configuration conf) throws IOException {
        super.initialize(uri, conf);
        Utils.dbgPrint("initialize");
        setConf(conf);
        this.uri = URI.create(uri.getScheme() + "://" + uri.getAuthority());
        Utils.dbgPrint("uri >", this.uri);
        // this.workingDir = new Path("/user", System.getProperty("user.name"));
        setWorkingDirectory(new Path("/user", System.getProperty("user.name")));
        Utils.dbgPrint("workingDir >", getWorkingDirectory());
        Utils.dbgPrint("Create System Store connector");

        if (hadoopPithosConnector == null) {
            setHadoopPithosConnector(new HadoopPithosConnector(
                    conf.get("fs.pithos.url"), conf.get("auth.pithos.token"),
                    conf.get("auth.pithos.uuid")));
        }

    }

    @Override
    public Path getWorkingDirectory() {
        Utils.dbgPrint("getWorkingDirectory", workingDir);
        return workingDir;
    }

    @Override
    public void setWorkingDirectory(Path dir) {
        workingDir = makeAbsolute(dir);
        Utils.dbgPrint("setWorkingDirectory >", workingDir);
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
        Utils.dbgPrint("append");
        throw new IOException("Not supported");
    }

    @Override
    public FSDataOutputStream create(Path f, FsPermission permission,
            boolean overwrite, int bufferSize, short replication,
            long blockSize, Progressable progress) throws IOException {

        // - Initialize & release previously allocated memory
        pithosOutputStreamInstance = null;
        fsDataOutputStreamInstance = null;

        pithosPath = new PithosPath(f);
        Utils.dbgPrint("create > container", pithosPath.getContainer());

        Utils.dbgPrint("create >", f, pithosPath, getHadoopPithosConnector()
                .getPithosBlockDefaultSize(pithosPath.getContainer()),
                bufferSize);

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

    @Override
    public boolean delete(Path f, boolean recursive) throws IOException {
        Utils.dbgPrint("delete > path, recurse ", f, recursive);
        pithosPath = new PithosPath(f);
        resp = getHadoopPithosConnector().deletePithosObject(
                pithosPath.getContainer(), pithosPath.getObjectAbsolutePath());
        if (resp.contains("204")) {
            Utils.dbgPrint("=================================================");
            Utils.dbgPrint("DELETE CALLED - SUCCESSFULLY");
            Utils.dbgPrint("=================================================");

            return true;
        }
        Utils.dbgPrint("=================================================");
        Utils.dbgPrint("DELETE CALLED - FAILED");
        Utils.dbgPrint("=================================================");

        return false;
    }

    @Override
    public boolean exists(Path f) throws IOException {
        // TODO only for testing, should re-use getFileStatus normally
        Utils.dbgPrint("exists", f);
        return super.exists(f);
    }

    @Override
    public PithosFileStatus getFileStatus(Path targetPath) throws IOException {
        Utils.dbgPrint("getFileStatus", "ENTRY");
        Utils.dbgPrint("targetPath >", targetPath);
        // - Process the given path
        pithosPath = new PithosPath(targetPath);
        Utils.dbgPrint("pithosPath >", pithosPath.getObjectAbsolutePath());

        // //////////////////////////////////////////////////////
        if (PithosOutputStream.closed) {

            String fromFolder = pithosPath.getObjectAbsolutePath();
            String toFolder = pithosPath.getObjectAbsolutePath().substring(0,
                    pithosPath.getObjectAbsolutePath().indexOf("/"));
            String resultFile = "part-r-00000";

            String copyFromFullPath = fromFolder.concat("/").concat(resultFile);
            String copyToFullPath = toFolder.concat("/").concat(resultFile);

            Utils.dbgPrint("=================================================");
            Utils.dbgPrint("MOVE RESULTS FOLDER");
            Utils.dbgPrint("=================================================");
            Utils.dbgPrint("FROM FOLDER --> " + fromFolder);
            Utils.dbgPrint("THE FILE --> " + resultFile);
            Utils.dbgPrint("FULL PATH FROM--> " + copyFromFullPath);
            Utils.dbgPrint("------------------------------");
            Utils.dbgPrint("TO FOLDER --> " + toFolder);
            Utils.dbgPrint("THE FILE --> " + "part-r-00000");
            Utils.dbgPrint("FULL PATH TO--> " + copyToFullPath);

            PithosFileSystem.getHadoopPithosConnector()
                    .movePithosObjectToFolder("pithos", // container
                            copyFromFullPath, // source object
                            "", // folder path
                            copyToFullPath); // target object

        }
        // //////////////////////////////////////////////////////

        urlEsc = null;
        try {
            urlEsc = Utils.urlEscape(null, null,
                    pithosPath.getObjectAbsolutePath(), null);
        } catch (URISyntaxException e) {
            Utils.dbgPrint("getFileStatus > invalid pithosPath");
            throw new IOException(e);
        }
        metadata = getHadoopPithosConnector().getPithosObjectMetaData(
                pithosPath.getContainer(), urlEsc, PithosResponseFormat.JSON);
        if (metadata.toString().contains("HTTP/1.1 404 NOT FOUND")) {
            Utils.dbgPrint("File does not exist in Pithos FS.");
            throw new FileNotFoundException("File does not exist in Pithos FS.");
        }
        for (String obj : metadata.getResponseData().keySet()) {
            if (obj != null
                    && (obj.matches("Content-Type") || obj
                            .matches("Content_Type"))) {
                for (String fileType : metadata.getResponseData().get(obj)) {
                    if (fileType.contains("application/directory")) {
                        isDir = true;
                        break;
                    } else {
                        isDir = false;
                    }
                }
            }
        }
        if (isDir) {
            pithosFileStatus = new PithosFileStatus(true,
                    DEFAULT_HDFS_BLOCK_SIZE, false, targetPath);
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

            pithosFileStatus = new PithosFileStatus(length,
                    DEFAULT_HDFS_BLOCK_SIZE, Utils.dateTimeToEpoch(
                            modificationTime, ""), targetPath);
        }
        Utils.dbgPrint("getFileStatus", "EXIT");
        Utils.dbgPrint("pithos_file_status >", pithosFileStatus);

        Utils.dbgPrint("=================================================");
        Utils.dbgPrint("GET FILE STATUS CALLED");
        Utils.dbgPrint("=================================================");

        return pithosFileStatus;
    }

    @Override
    public FileStatus[] listStatus(Path f) throws IOException {
        Utils.dbgPrint("listStatus > path", f);

        filename = "";
        pithosPath = new PithosPath(f);
        pathToString = pithosPath.toString();

        pathToString = pathToString.substring(this.getScheme().toString()
                .concat("://").length());

        Utils.dbgPrint("listStatus > pathToString", pathToString);
        filesList = pathToString.split("/");
        filename = filesList[filesList.length - 1];
        Utils.dbgPrint("listStatus > 1. filename", filename);
        int count = 2;
        while (!filesList[filesList.length - count].equals(pithosPath
                .getContainer())) {
            filename = filesList[filesList.length - count] + "/" + filename;
            count++;
        }
        Utils.dbgPrint("listStatus > 2. filename", filename);
        // results = Collections.synchronizedList(new ArrayList<FileStatus>());
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
        for (int i = 0; i < results.toArray(resultsArr).length; i++) {
            Utils.dbgPrint("listStatus results >", i, resultsArr[i]);
        }

        Utils.dbgPrint("=================================================");
        Utils.dbgPrint("LIST STATUS CALLED");
        Utils.dbgPrint("=================================================");

        return results.toArray(resultsArr);
    }

    @Override
    public boolean mkdirs(Path f, FsPermission permission) throws IOException {
        Utils.dbgPrint("mkdirs path >", f);
        pithosPath = new PithosPath(f);
        Utils.dbgPrint("mkdirs pithosPath >",
                pithosPath.getObjectFolderAbsolutePath());
        Utils.dbgPrint("mkdirs > uploadFileToPithos > ",
                pithosPath.getContainer(),
                pithosPath.getObjectFolderAbsolutePath(), true);
        resp = getHadoopPithosConnector().uploadFileToPithos(
                pithosPath.getContainer(),
                pithosPath.getObjectFolderAbsolutePath(), true);

        if (resp != null && resp.contains("201")) {
            return true;
        }
        Utils.dbgPrint("mkdirs> response:", resp);
        return false;
    }

    @Override
    public FSDataInputStream open(Path targetFile, int bufferSize)
            throws IOException {
        pithosPath = new PithosPath(targetFile);
        pathEsc = null;
        try {
            pathEsc = Utils.urlEscape(null, null,
                    pithosPath.getObjectAbsolutePath(), null);
        } catch (URISyntaxException e) {
            Utils.dbgPrint("open > invalid targetFile");
            throw new IOException(e);
        }

        return getHadoopPithosConnector().pithosObjectInputStream(
                pithosPath.getContainer(), pathEsc);
    }

    @Override
    public boolean rename(Path src, Path dst) throws IOException {
        Utils.dbgPrint("rename", src, dst);
        srcPiPath = new PithosPath(src);
        dstPiPath = new PithosPath(dst);
        srcName = srcPiPath.getObjectAbsolutePath();
        dstName = dstPiPath.getObjectAbsolutePath();
        Utils.dbgPrint("rename src, dst", srcName, dstName);
        resp = getHadoopPithosConnector().movePithosObjectToFolder(
                srcPiPath.getContainer(), srcName, "", dstName);
        Utils.dbgPrint("rename resp>", resp);

        Utils.dbgPrint("=================================================");
        Utils.dbgPrint("RENAME CALLED");
        Utils.dbgPrint("=================================================");

        if (resp.contains("201")) {
            return true;
        } else {
            return false;
        }
    }

    /**
     * 
     * @param args
     */
    public static void main(String[] args) {
        // Stub so we can create a 'runnable jar' export for packing
        // dependencies
        String out = null;
        String hashAlgo = "SHA-256";
        try {
            out = Utils.computeHash("Lorem ipsum dolor sit amet.", hashAlgo);
        } catch (NoSuchAlgorithmException e) {
            Utils.dbgPrint("invalid hash algorithm:" + hashAlgo, e);
        } catch (UnsupportedEncodingException e) {
            Utils.dbgPrint("invalid encoding", e);
        }
        Utils.dbgPrint("Pithos FileSystem Connector loaded.");
        Utils.dbgPrint("Hash Test:", out);
    }

}
