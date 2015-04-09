package gr.grnet.escience.fs.pithos;

import org.apache.hadoop.fs.Path;

public class PithosPath {

	private String container;
	private String object_name;
	private String object_absolute_path;
	private String folder_absolute_path;
	private PithosFileSystem pithosFs = new PithosFileSystem();
	private Path pithosFSPath;
	private String fsPathStr;
	private String[] pathParts;

	public PithosPath() {
	}

	public PithosPath(Path hadoopPath) {
		this.pithosFSPath = hadoopPath;
		convertHadoopFSPathToPithosFSPath(getPithosFSPath());
	}

	public PithosPath(String pithos_container,
			String pithos_object_absolute_path) {
		this.container = pithos_container;
		this.object_absolute_path = pithos_object_absolute_path;

		// - If the given object absolute path does not refer to folder, then
		// extract file name if exists
		if (getObjectAbsolutePath().contains("/")) {
			if (!getObjectAbsolutePath().endsWith("/")) {
				// - Get the folder absolute path
				this.folder_absolute_path = getObjectAbsolutePath().substring(
						0, getObjectAbsolutePath().lastIndexOf("/"));
				// - Get the actual name of the object
				this.object_name = getObjectAbsolutePath().substring(
						getObjectFolderAbsolutePath().length() + 1);

			}
		} else {
			this.folder_absolute_path = "";
			this.object_name = getObjectAbsolutePath();
		}
	}

	private void convertHadoopFSPathToPithosFSPath(Path hadoopPath) {
		fsPathStr = hadoopPath.toString();

		fsPathStr = fsPathStr.substring(pithosFs.getScheme().toString()
				.concat("://").length());

		pathParts = fsPathStr.split("/");

		this.container = pathParts[0];
		this.object_absolute_path = fsPathStr
				.substring(getContainer().length() + 1);

		// - If the given object absolute path does not refer to folder, then
		// extract file name if exists
		if (getObjectAbsolutePath().contains("/")) {
			if (!getObjectAbsolutePath().endsWith("/")) {
				// - Get the folder absolute path
				this.folder_absolute_path = getObjectAbsolutePath().substring(
						0, getObjectAbsolutePath().lastIndexOf("/"));
				// - Get the actual name of the object
				this.object_name = getObjectAbsolutePath().substring(
						getObjectFolderAbsolutePath().length() + 1);

			}
		} else {
			this.folder_absolute_path = "";
			this.object_name = getObjectAbsolutePath();
		}
	}

	public String getContainer() {
		return container;
	}

	public void setContainer(String container) {
		this.container = container;
	}

	public String getObjectAbsolutePath() {
		return object_absolute_path;
	}

	public void setObjectAbsolutePath(String object_path) {
		this.object_absolute_path = object_path;
	}

	public String getObjectFolderAbsolutePath() {
		return folder_absolute_path;
	}

	public void setObjectFolderAbsolutePath(String folder_path) {
		this.folder_absolute_path = folder_path;
	}

	public String getObjectName() {
		return object_name;
	}

	public void setObjectName(String object_name) {
		this.object_name = object_name;
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