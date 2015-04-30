package gr.grnet.escience.hdfs.client;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.security.PrivilegedExceptionAction;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.BlockLocation;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.security.UserGroupInformation;

/**
 * This class implements a java-based HDFS Client that can perform actions such
 * as: - add file on the HDFS - read file from HDFS - delete file from HDFS -
 * create directory on hdfs
 * 
 * @since March, 2015
 * @author Dimitris G. Kelaidonis (kelaidonis@gmail.com)
 * @version 0.1
 * 
 */
public class OrkaHdfsClient {

    private final Configuration conf = new Configuration();
    private UserGroupInformation ugi;

    /** Constructor **/
    public OrkaHdfsClient() {

        /** Create Hadoop FS configuration **/
        getConfiguration().set("fs.defaultFS", "fs.defaultFS");
        getConfiguration().set("hadoop.job.ugi", "hadoop.job.ugi");

        // - Create User Group info
        setUserGroupInformation(UserGroupInformation
                .createRemoteUser("hadoop.job.ugi"));
    }

    /** Get current configuration instance **/
    private Configuration getConfiguration() {
        return conf;
    }

    /** Get user group for hadoop **/
    private UserGroupInformation getUserGroupInformation() {
        return ugi;
    }

    /** Create ugi instance **/
    private void setUserGroupInformation(UserGroupInformation _ugi) {
        this.ugi = _ugi;
    }

    /****
     * Implements a FSDataOutputSteam that adds a file to the HDFS
     * 
     * @param {source: the path of the source file, dest: the path of the
     *        destination file}
     * @throws InterruptedException
     * 
     ***/
    public void uploadToHdfs(final String source, final String dest)
            throws IOException, InterruptedException {
        /** Perform the action as the user in the defined hadoop user group **/
        getUserGroupInformation().doAs(new PrivilegedExceptionAction<Void>() {
            @Override
            public Void run() throws Exception {
                // - Create instance for the FS
                FileSystem fileSystem = FileSystem.get(getConfiguration());

                // - Check if the source file exists
                if (!(new File(source)).exists()) {
                    System.out.println("Source File <" + source
                            + "> does not exist");
                    return null;
                }

                // - Get the filename out of the file path
                String filename = source.substring(source.lastIndexOf('/') + 1,
                        source.length());

                // - Create the destination path including the filename.
                String dest_tmp = dest;
                if (dest_tmp.charAt(dest.length() - 1) != '/') {
                    dest_tmp = dest_tmp + "/" + filename;
                } else {
                    dest_tmp = dest_tmp + filename;
                }

                System.out.println("Adding file to " + dest_tmp);

                // - Check if the file already exists
                Path destPath = new Path(dest_tmp);
                if (fileSystem.exists(destPath)) {
                    System.out.println("File " + dest_tmp + " already exists");
                    return null;
                }

                /** Create a new file on FS and write data to it **/
                // - Create an FSOutputStream to the FS
                FSDataOutputStream out = fileSystem.create(destPath);
                // - Create a (Java) InputStream for the source file
                InputStream in = new BufferedInputStream(new FileInputStream(
                        new File(source)));
                // - Define buffer size
                byte[] buffer = new byte[2048];
                int numBytes = 0;

                // - Write byte on the file in the FS
                while ((numBytes = in.read(buffer)) > 0) {
                    out.write(buffer, 0, numBytes);
                }

                // - Close streams & FS
                in.close();
                out.close();
                fileSystem.close();

                return null;
            }
        });
    }

    /****
     * Implements a FSDataInputSteam that gets the data of a file in the HDFS
     * 
     * @param {file: the filename or full filepath of the file}
     * @throws InterruptedException
     * 
     ***/
    public void readFromHdfs(final String file) throws IOException,
            InterruptedException {
        /** Perform the action as the user in the defined hadoop user group **/
        getUserGroupInformation().doAs(new PrivilegedExceptionAction<Void>() {
            @Override
            public Void run() throws Exception {
                // - Create instance for the FS
                FileSystem fileSystem = FileSystem.get(getConfiguration());

                // - Check if the requested file exists
                Path path = new Path(file);
                if (!fileSystem.exists(path)) {
                    System.out.println("File <" + file + "> does not exists");
                    return null;
                }

                // - Create a FSInputStream so as to stream data from the HDFS
                FSDataInputStream in = fileSystem.open(path);

                // - Create a local temp file for the streaming of data
                String filename = file.substring(file.lastIndexOf('/') + 1,
                        file.length());
                // - Write data on the local temp file
                OutputStream out = new BufferedOutputStream(
                        new FileOutputStream(new File(filename)));

                // - Define buffer size
                byte[] buffer = new byte[2048];
                int numBytes = 0;

                // - Write byte on the file in the FS
                while ((numBytes = in.read(buffer)) > 0) {
                    out.write(buffer, 0, numBytes);
                }

                // - Close streams & FS
                in.close();
                out.close();
                fileSystem.close();

                return null;
            }
        });
    }

    /****
     * Implements a Delete action that performs delete on the HDFS
     * 
     * @param {file: the filename of the file want to delete}
     * @throws InterruptedException
     * 
     ***/
    public void deleteFromHdfs(final String file) throws IOException,
            InterruptedException {
        /** Perform the action as the user in the defined hadoop user group **/
        getUserGroupInformation().doAs(new PrivilegedExceptionAction<Void>() {
            @Override
            public Void run() throws Exception {
                // - Create instance for the FS
                FileSystem fileSystem = FileSystem.get(getConfiguration());

                // - Check if the requested file exists
                Path path = new Path(file);
                if (!fileSystem.exists(path)) {
                    System.out.println("File <" + file + "> does not exists");
                    return null;
                }

                // - Perform the delete action
                fileSystem.delete(new Path(file), true);

                // - Close FS
                fileSystem.close();

                return null;
            }
        });
    }

    /****
     * Implements a directory creation action on the HDFS
     * 
     * @param {dir: the directory name on the HDFS}
     * @throws IOException
     * @throws InterruptedException
     * 
     ***/
    public void mkdir(final String dir) throws IOException,
            InterruptedException {
        /** Perform the action as the user in the defined hadoop user group **/
        getUserGroupInformation().doAs(new PrivilegedExceptionAction<Void>() {
            @Override
            public Void run() throws Exception {
                // - Create instance for the FS
                FileSystem fileSystem = FileSystem.get(getConfiguration());

                // - Check if the directory exists
                Path path = new Path(dir);
                if (fileSystem.exists(path)) {
                    System.out.println("Directory <" + dir
                            + "> already not exists");
                    return null;
                }

                // - Perform the creation action
                fileSystem.mkdirs(path);

                // - Close the FS
                fileSystem.close();

                return null;
            }
        });
    }

    /****
     * Implements a copy from local to HDFS process Hadoop cmd:
     * "# hadoop fs -copyFromLocal <local fs> <hadoop fs>"
     * 
     * @param {source: the path of the source file, dest: the path of the
     *        destination file}
     * @throws InterruptedException
     ***/
    public void copyFromLocalToHdfs(final String source, final String dest)
            throws IOException, InterruptedException {
        /** Perform the action as the user in the defined hadoop user group **/
        getUserGroupInformation().doAs(new PrivilegedExceptionAction<Void>() {
            @Override
            public Void run() throws Exception {
                // - Create instance for the FS
                FileSystem fileSystem = FileSystem.get(getConfiguration());

                // - Check if the file already exists
                Path srcPath = new Path(source);
                if (!(fileSystem.exists(srcPath))) {
                    System.out.println("No such source " + srcPath);
                    return null;
                }

                // - Check if destination file already exists
                Path dstPath = new Path(dest);
                if (!(fileSystem.exists(dstPath))) {
                    System.out.println("No such destination " + dstPath);
                    return null;
                }

                // - Get the filename out of the file path
                String filename = source.substring(source.lastIndexOf('/') + 1,
                        source.length());

                // - Perform the copy by using the Hadoop API native methods
                try {
                    fileSystem.copyFromLocalFile(srcPath, dstPath);
                    System.out
                            .println("File " + filename + "copied to " + dest);
                } catch (Exception e) {
                    System.err.println("Exception caught! :" + e);

                } finally {
                    fileSystem.close();
                }
                return null;
            }
        });
    }

    /****
     * Implements a copy from HDFS to local process Hadoop cmd:
     * "# hadoop fs -copyToLocal <hadoop fs> <local fs>"
     * 
     * @param {source: the path of the source file, dest: the path of the
     *        destination file}
     * @throws InterruptedException
     * 
     ***/
    public void downloadFromHdfs(final String source, final String dest)
            throws IOException, InterruptedException {
        /** Perform the action as the user in the defined hadoop user group **/
        getUserGroupInformation().doAs(new PrivilegedExceptionAction<Void>() {
            @Override
            public Void run() throws Exception {
                // - Create instance for the FS
                FileSystem fileSystem = FileSystem.get(getConfiguration());

                // - Check if the file already exists
                Path srcPath = new Path(source);
                if (!(fileSystem.exists(srcPath))) {
                    System.out.println("No such source " + srcPath);
                    return null;
                }

                // - Check if the destination already exists
                Path dstPath = new Path(dest);
                if (!(fileSystem.exists(dstPath))) {
                    System.out.println("No such destination " + dstPath);
                    return null;
                }

                // - Get the filename out of the file path
                String filename = source.substring(source.lastIndexOf('/') + 1,
                        source.length());

                // - Perform the copy by using the Hadoop API native methods
                try {
                    fileSystem.copyToLocalFile(srcPath, dstPath);
                    System.out.println("File <" + filename + "> dowloaded to "
                            + dest);
                } catch (Exception e) {
                    System.err.println("Exception caught! :" + e);
                } finally {
                    fileSystem.close();
                }
                return null;
            }
        });
    }

    /****
     * Implements a rename action to a file on the HDFS cmd:
     * "# hadoop fs -mv <this name> <new name>"
     * 
     * @param {currentName: the current name of the file, newName: the new name
     *        of the file}
     * @throws IOException
     * @throws InterruptedException
     * 
     ***/
    public void renameFile(final String currentName, final String newName)
            throws IOException, InterruptedException {
        /** Perform the action as the user in the defined hadoop user group **/
        getUserGroupInformation().doAs(new PrivilegedExceptionAction<Void>() {
            @Override
            public Void run() throws Exception {
                // - Create instance for the FS
                FileSystem fileSystem = FileSystem.get(getConfiguration());
                // - Check if the file want to rename exists
                Path fromPath = new Path(currentName);
                if (!(fileSystem.exists(fromPath))) {
                    System.out.println("No such destination " + fromPath);
                    return null;
                }

                // - Check if a file already exists with the required name
                Path toPath = new Path(newName);
                if (fileSystem.exists(toPath)) {
                    System.out.println("Already exists! " + toPath);
                    return null;
                }

                // - Perform the rename action by using the Hadoop API native
                // methods
                try {
                    boolean isRenamed = fileSystem.rename(fromPath, toPath);
                    if (isRenamed) {
                        System.out.println("Renamed from " + currentName
                                + "to " + newName);
                    }
                } catch (Exception e) {
                    System.out.println("Exception :" + e);
                } finally {
                    fileSystem.close();
                }
                return null;
            }
        });
    }

    /****
     * Get the location of the blocks on the HDFS
     * 
     * @param {source: the file on the HDFS}
     * @throws InterruptedException
     * 
     ***/
    public void getBlockLocations(final String source) throws IOException,
            InterruptedException {
        /** Perform the action as the user in the defined hadoop user group **/
        getUserGroupInformation().doAs(new PrivilegedExceptionAction<Void>() {
            @Override
            public Void run() throws Exception {
                // - Create instance for the FS
                FileSystem fileSystem = FileSystem.get(getConfiguration());

                // - Check if the file already exists
                Path srcPath = new Path(source);
                if (!(fileSystem.exists(srcPath))) {
                    System.out.println("No such destination " + srcPath);
                    return null;
                }
                // Get the filename out of the file path
                String filename = source.substring(source.lastIndexOf('/') + 1,
                        source.length());

                FileStatus fileStatus = fileSystem.getFileStatus(srcPath);

                BlockLocation[] blkLocations = fileSystem
                        .getFileBlockLocations(fileStatus, 0,
                                fileStatus.getLen());
                int blkCount = blkLocations.length;

                System.out.println("File :" + filename + "stored at:");
                for (int i = 0; i < blkCount; i++) {
                    String[] hosts = blkLocations[i].getHosts();
                    System.out.format("Host %d: %s %n", i, hosts);
                }
                return null;
            }
        });
    }

}
