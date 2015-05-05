package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.commons.Utils;

import java.io.FileNotFoundException;

import org.apache.hadoop.fs.Path;

public class PithosPath {

    private String container;
    private String objectName;
    private String objectAbsolutePath;
    private String folderAbsolutePath;
    private PithosFileSystem pithosFs = new PithosFileSystem();
    private Path pithosFSPath;
    private String fsPathStr;

    // private String[] pathParts;

    public PithosPath() {
    }

    public PithosPath(Path hadoopPath) throws FileNotFoundException {
        this.pithosFSPath = hadoopPath;
        convertHadoopFSPathToPithosFSPath(getPithosFSPath());
    }

    public PithosPath(String pithosContainer, String pithosObjectPath) {
        // TODO Do not parse the path as a string, instead use Path api
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

    private void convertHadoopFSPathToPithosFSPath(Path givenPath) {

        Utils util = new Utils();
        String givenPath_str = givenPath.toString();
        util.dbgPrint("-------------------| CONVERT |-------------------");
        util.dbgPrint("1. INITIAL GIVEN PATH --> ", givenPath_str);

        // - Check if contains scheme and remove it
        if (givenPath_str.contains("://")) {
            givenPath_str = givenPath_str.substring(pithosFs.getScheme()
                    .toString().concat("://").length());
        }
        util.dbgPrint("2. GIVEN PATH WITHOUT SCHEME --> ", givenPath_str);

        // - Get the defined container
        this.container = givenPath_str.substring(0, givenPath_str.indexOf("/"));

        this.objectAbsolutePath = givenPath_str.substring(getContainer()
                .length() + 1);

        util.dbgPrint("3. OBEJCT ABSOLUTE PATH --> ", getObjectAbsolutePath());

        // - Check what is requested in terms of files and directories on Pithos
        // FS
        if (getObjectAbsolutePath().contains("/")) {
            // - check if it is not a directory
            if (!getObjectAbsolutePath().endsWith("/")) {
                // - Extract only the pithos path to the directory on pithos FS
                this.folderAbsolutePath = getObjectAbsolutePath().substring(0,
                        getObjectAbsolutePath().lastIndexOf("/"));
                // - Essentially the object name for Pithos FS is the extracted
                // absolute path
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

        util.dbgPrint("4. OBJECT NAME --> ", getObjectName());

        util.dbgPrint("5. FOLDER ABSOLUTE PATH --> ",
                getObjectFolderAbsolutePath());

        util.dbgPrint("--------------------------------------------------");

        // fsPathStr = hadoopPath.toString();
        //
        // if (!fsPathStr.contains("._COPYING_")) {
        // fsPathStr = fsPathStr.concat("._COPYING_");
        // }
        //
        // Utils util = new Utils();
        //
        // util.dbgPrint("THE GIVEN HADOOP PATH IS--> ", fsPathStr);
        //
        // fsPathStr = fsPathStr.substring(pithosFs.getScheme().toString()
        // .concat("://").length());
        //
        // pathParts = fsPathStr.split("/");
        //
        // this.container = pathParts[0];
        // this.objectAbsolutePath = fsPathStr
        // .substring(getContainer().length() + 1);
        //
        // // - If the given object absolute path does not refer to folder, then
        // // extract file name if exists
        // if (getObjectAbsolutePath().contains("/")) {
        // if (!getObjectAbsolutePath().endsWith("/")) { // - Get the folder
        // // absolute path
        // this.folderAbsolutePath = getObjectAbsolutePath().substring(0,
        // getObjectAbsolutePath().lastIndexOf("/"));
        // // - Get the actual name of the object
        // this.objectName = getObjectAbsolutePath().substring(
        // getObjectFolderAbsolutePath().length() + 1);
        //
        // }
        // } else {
        // this.folderAbsolutePath = "";
        // this.objectName = getObjectAbsolutePath();
        // }
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

    public Path createFSPath() {
        fsPathStr = pithosFs.getScheme().concat("://").concat(getContainer())
                .concat("/").concat(getObjectAbsolutePath());

        this.pithosFSPath = new Path(fsPathStr);

        return getPithosFSPath();
    }

    public Path getPithosFSPath() {
        return pithosFSPath;
    }

    @Override
    public String toString() {
        return getPithosFSPath().toString();
    }

}