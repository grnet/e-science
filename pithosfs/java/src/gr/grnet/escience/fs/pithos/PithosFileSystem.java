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
    private static long defaultBlockSize = (long) 128 * 1024 * 1024;
    private Path workingDir;
    private String pathToString;
    private PithosPath pithosPath;
    static String filename;

    private String[] filesList;
    private boolean isDir = false;
    private long length = 0;
    private PithosFileStatus pithosFileStatus;
    private final Utils util = new Utils();

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
            HadoopPithosConnector hadoopPithosConnector) {
        PithosFileSystem.hadoopPithosConnector = hadoopPithosConnector;
    }

    @Override
    public String getScheme() {
        util.dbgPrint("getScheme >", "pithos");
        return "pithos";
    }

    @Override
    public URI getUri() {
        util.dbgPrint("getUri >", uri);
        return uri;
    }

    @Override
    public void initialize(URI uri, Configuration conf) throws IOException {
        super.initialize(uri, conf);
        util.dbgPrint("initialize");
        setConf(conf);
        this.uri = URI.create(uri.getScheme() + "://" + uri.getAuthority());
        util.dbgPrint("uri >", this.uri);
        this.workingDir = new Path("/user", System.getProperty("user.name"));
        util.dbgPrint("workingDir >", this.workingDir);
        util.dbgPrint("Create System Store connector");

        if (hadoopPithosConnector == null) {
            this.hadoopPithosConnector = new HadoopPithosConnector(
                    conf.get("fs.pithos.url"), conf.get("auth.pithos.token"),
                    conf.get("auth.pithos.uuid"));
        }

    }

    @Override
    public Path getWorkingDirectory() {
        util.dbgPrint("getWorkingDirectory", workingDir);
        return workingDir;
    }

    @Override
    public void setWorkingDirectory(Path dir) {
        workingDir = makeAbsolute(dir);
        util.dbgPrint("setWorkingDirectory >", workingDir);
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
        util.dbgPrint("append");
        throw new IOException("Not supported");
    }

    @Override
    public long getDefaultBlockSize() {
        util.dbgPrint("getDefaultBlockSize >",
                getConf().getLongBytes("dfs.blocksize", defaultBlockSize));
        return getConf().getLongBytes("dfs.blocksize", defaultBlockSize);
    }

    @Override
    public String getCanonicalServiceName() {
        util.dbgPrint("getCanonicalServiceName");
        // Does not support Token
        return null;
    }

    @Override
    public FSDataOutputStream create(Path f, FsPermission permission,
            boolean overwrite, int bufferSize, short replication,
            long blockSize, Progressable progress) throws IOException {
        util.dbgPrint("create >", f, pithosPath, blockSize, bufferSize);
        return new FSDataOutputStream(new PithosOutputStream(getConf(),
                pithosPath, blockSize, bufferSize), statistics);
    }

    @Override
    public boolean delete(Path f, boolean recursive) throws IOException {
        util.dbgPrint("delete", f);
        // TODO Auto-generated method stub
        return false;
    }

    @Override
    public boolean exists(Path f) throws IOException {
        // TODO only for testing, should re-use getFileStatus normally
        util.dbgPrint("exists", f);
        return super.exists(f);
    }

    public boolean containerExistance(String container) {
        PithosResponse containerInfo = this.hadoopPithosConnector
                .getContainerInfo(container);
        return containerInfo.toString().contains("HTTP/1.1 404 NOT FOUND");
    }

    @Override
    public PithosFileStatus getFileStatus(Path targetPath) throws IOException {
        util.dbgPrint("getFileStatus", "ENTRY");
        util.dbgPrint("targetPath >", targetPath);
        // - Process the given path
        pithosPath = new PithosPath(targetPath);
        util.dbgPrint("pithosPath >", pithosPath.getObjectAbsolutePath());
        String urlEsc = null;
        try {
            urlEsc = util.urlEscape(null, null,
                    pithosPath.getObjectAbsolutePath(), null);
        } catch (URISyntaxException e) {
            util.dbgPrint("getFileStatus > invalid pithosPath");
            throw new IOException(e);
        }
        PithosResponse metadata = this.hadoopPithosConnector
                .getPithosObjectMetaData(pithosPath.getContainer(), urlEsc,
                        PithosResponseFormat.JSON);
        if (metadata.toString().contains("HTTP/1.1 404 NOT FOUND")) {
            util.dbgPrint("File does not exist in Pithos FS. (If filename contains spaces, add Quotation Marks)");
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
            pithosFileStatus = new PithosFileStatus(true, 0L, false, targetPath);
        } else {
            for (String obj : metadata.getResponseData().keySet()) {
                if (obj != null && obj.matches("Content-Length")) {
                    for (String lengthStr : metadata.getResponseData().get(obj)) {
                        length = Long.parseLong(lengthStr);
                    }
                }
            }
            String modificationTime = metadata.getResponseData().get("Last-Modified").get(0);
            pithosFileStatus = new PithosFileStatus(length,
                    getDefaultBlockSize(), util.dateTimeToEpoch(modificationTime, ""), targetPath);
        }
        util.dbgPrint("getFileStatus", "EXIT");
        util.dbgPrint("pithos_file_status >", pithosFileStatus);
        return pithosFileStatus;
    }

    @Override
    public FileStatus[] listStatus(Path f) throws IOException {
        util.dbgPrint("listStatus");

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

        ArrayList<FileStatus> results = new ArrayList<FileStatus>();
        FileStatus fileStatus;

        String[] files = this.hadoopPithosConnector.getFileList(
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
        util.dbgPrint("listStatus >",results);
        // - Return the list of the available files
        FileStatus [] resultsArr = new FileStatus[results.size()];
        return results.toArray(resultsArr);
    }

    @Override
    public boolean mkdirs(Path f, FsPermission permission) throws IOException {
        util.dbgPrint("mkdirs");
        // TODO Auto-generated method stub
        return false;
    }

    @Override
    public FSDataInputStream open(Path targetFile, int bufferSize)
            throws IOException {
        pithosPath = new PithosPath(targetFile);

        String pathEsc = null;
        try {
            pathEsc = util.urlEscape(null, null,
                    pithosPath.getObjectAbsolutePath(), null);
        } catch (URISyntaxException e) {
            util.dbgPrint("open > invalid targetFile");
            throw new IOException(e);
        }

        return this.hadoopPithosConnector.pithosObjectInputStream(
                pithosPath.getContainer(), pathEsc);
    }

    @Override
    public boolean rename(Path src, Path dst) throws IOException {
        util.dbgPrint("rename", src, dst);
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
        String hashAlgo = "SHA-256";
        try {
            out = util.computeHash("Lorem ipsum dolor sit amet.", hashAlgo);
        } catch (NoSuchAlgorithmException e) {
            util.dbgPrint("invalid hash algorithm:" + hashAlgo, e);
        } catch (UnsupportedEncodingException e) {
            util.dbgPrint("invalid encoding", e);
        }
        util.dbgPrint("Pithos FileSystem Connector loaded.");
        util.dbgPrint("Hash Test:", out);
    }

}
