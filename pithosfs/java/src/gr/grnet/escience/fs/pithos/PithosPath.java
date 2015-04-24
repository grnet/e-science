package gr.grnet.escience.fs.pithos;

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
	private String[] pathParts;

	public PithosPath() {
	}

	public PithosPath(Path hadoopPath) throws FileNotFoundException {
		this.pithosFSPath = hadoopPath;
		convertHadoopFSPathToPithosFSPath(getPithosFSPath());
	}

	public PithosPath(String pithosContainer, String pithosObjectPath) {
		this.container = pithosContainer;
		this.objectAbsolutePath = pithosObjectPath;

		// - If the given object absolute path does not refer to folder, then
		// extract file name if exists
		if (getObjectAbsolutePath().contains("/")) {
			if (!getObjectAbsolutePath().endsWith("/")) {
				// - Get the folder absolute path
				this.folderAbsolutePath = getObjectAbsolutePath().substring(
						0, getObjectAbsolutePath().lastIndexOf("/"));
				// - Get the actual name of the object
				this.objectName = getObjectAbsolutePath().substring(
						getObjectFolderAbsolutePath().length() + 1);

			}
		} else {
			this.folderAbsolutePath = "";
			this.objectName = getObjectAbsolutePath();
		}
	}

	private void convertHadoopFSPathToPithosFSPath(Path hadoopPath) {
		fsPathStr = hadoopPath.toString();

		fsPathStr = fsPathStr.substring(pithosFs.getScheme().toString()
				.concat("://").length());

		pathParts = fsPathStr.split("/");

		this.container = pathParts[0];
		this.objectAbsolutePath = fsPathStr
				.substring(getContainer().length() + 1);

		// - If the given object absolute path does not refer to folder, then
		// extract file name if exists
		if (getObjectAbsolutePath().contains("/")) {
			if (!getObjectAbsolutePath().endsWith("/")) {
				// - Get the folder absolute path
				this.folderAbsolutePath = getObjectAbsolutePath().substring(
						0, getObjectAbsolutePath().lastIndexOf("/"));
				// - Get the actual name of the object
				this.objectName = getObjectAbsolutePath().substring(
						getObjectFolderAbsolutePath().length() + 1);

			}
		} else {
			this.folderAbsolutePath = "";
			this.objectName = getObjectAbsolutePath();
		}
	}

	public String getContainer() {
		return container;
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