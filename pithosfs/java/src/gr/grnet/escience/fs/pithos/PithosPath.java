package gr.grnet.escience.fs.pithos;

import java.io.FileNotFoundException;

import org.apache.hadoop.fs.Path;

/**
 * Produce a pithos path structure from an HDFS path reference or pithos path
 * components Used with Hadoop FS API.
 */
public class PithosPath {

    private String container;

    private String objectName;

    private String objectAbsolutePath;

    private String folderAbsolutePath;

    private PithosFileSystem pithosFs = new PithosFileSystem();

    private Path pithosFsPath;

    private String hdfsPathStr;

    /** The given path str. */
    private String givenPathStr = null;

    /**
     * Instantiates an empty pithos path.
     */
    public PithosPath() {
    }

    /**
     * Instantiates a new pithos path from hadoop path.
     *
     * @param hadoopPath
     *            the hadoop path
     * @throws FileNotFoundException
     */
    public PithosPath(Path hadoopPath) throws FileNotFoundException {
        this.pithosFsPath = hadoopPath;
        convertHadoopFSPathToPithosFSPath(getPithosFSPath());
    }

    /**
     * Instantiates a new pithos path.
     *
     * @param pithosContainer
     *            the pithos container
     * @param pithosObjectPath
     *            the pithos object path
     */
    public PithosPath(String pithosContainer, String pithosObjectPath) {
        // Do not parse the path as a string, instead use Path api
        // and take into account type of requested resource and pithos container
        // / authority elements.
        this.container = pithosContainer;
        this.objectAbsolutePath = pithosObjectPath;

        // - If the given object absolute path does not refer to folder, then
        // extract file name if exists
        if (getObjectAbsolutePath().contains("/")) {
            if (!getObjectAbsolutePath().endsWith("/")) {
                // - Get the folder absolute path
                this.folderAbsolutePath = getObjectAbsolutePath().substring(0,
                        getObjectAbsolutePath().lastIndexOf("/"));
                // - Get the actual name of the object
                this.objectName = getObjectAbsolutePath().substring(
                        getObjectFolderAbsolutePath().length() + 1);

            }
        } else {
            this.folderAbsolutePath = "";
            this.objectName = getObjectAbsolutePath();
        }
    }

    /**
     * Convert hadoop fs path to pithos fs path.
     *
     * @param givenPath
     *            the given path
     */
    private void convertHadoopFSPathToPithosFSPath(Path givenPath) {

        givenPathStr = givenPath.toString();

        // - Check if contains scheme and remove it
        if (givenPathStr.contains("://")) {
            givenPathStr = givenPathStr.substring(pithosFs.getScheme()
                    .toString().concat("://").length());
        }

        // - Get the defined container
        this.container = givenPathStr.substring(0, givenPathStr.indexOf("/"));

        this.objectAbsolutePath = givenPathStr.substring(getContainer()
                .length() + 1);

        // - Check what is requested in terms of files and directories on Pithos
        // FS
        if (getObjectAbsolutePath().contains("/")) {
            // - check if it is not a directory
            if (!getObjectAbsolutePath().endsWith("/")) {
                // - Extract only the pithos path to the directory on pithos FS
                this.folderAbsolutePath = getObjectAbsolutePath().substring(0,
                        getObjectAbsolutePath().lastIndexOf("/"));
                // object name for Pithos FS is the extracted absolute path
                this.objectName = getObjectAbsolutePath();

            }
            // - else if it is a directory
            else {
                // - Get the path of the directory specified
                this.folderAbsolutePath = getObjectAbsolutePath().substring(
                        getObjectAbsolutePath().lastIndexOf("/") + 1,
                        getObjectAbsolutePath().length());

                // - Essentially the object name for Pithos FS is the extracted
                // absolute path
                this.objectName = getObjectAbsolutePath();
            }
        } else {
            // - Essentially the object name for Pithos FS is the extracted
            // absolute path
            this.objectName = getObjectAbsolutePath();
        }

    }

    public String getContainer() {
        return container;
    }

    public String getParent() {
        return this.folderAbsolutePath;
    }

    public void setContainer(String container) {
        this.container = container;
    }

    public String getObjectAbsolutePath() {
        return objectAbsolutePath;
    }

    public void setObjectAbsolutePath(String objectPath) {
        this.objectAbsolutePath = objectPath;
    }

    public String getObjectFolderAbsolutePath() {
        return folderAbsolutePath;
    }

    public void setObjectFolderAbsolutePath(String folderPath) {
        this.folderAbsolutePath = folderPath;
    }

    public String getObjectName() {
        return objectName;
    }

    public void setObjectName(String objectName) {
        this.objectName = objectName;
    }

    /**
     * Creates the full pithosFS path from object path and default components.
     *
     * @return the path
     */
    public Path createFSPath() {
        hdfsPathStr = pithosFs.getScheme().concat("://").concat(getContainer())
                .concat("/").concat(getObjectAbsolutePath());

        this.pithosFsPath = new Path(hdfsPathStr);

        return getPithosFSPath();
    }

    public Path getPithosFSPath() {
        return pithosFsPath;
    }

    /*
     * (non-Javadoc)
     * 
     * @see java.lang.Object#toString()
     */
    @Override
    public String toString() {
        return getPithosFSPath().toString();
    }

}