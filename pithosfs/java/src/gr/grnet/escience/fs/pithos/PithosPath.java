package gr.grnet.escience.fs.pithos;

import org.apache.hadoop.fs.Path;

public class PithosPath {

	private String container;
	private String object_path;
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

	public PithosPath(String pithos_container, String pithos_object_path) {
		this.container = pithos_container;
		this.object_path = pithos_object_path;
	}

	private void convertHadoopFSPathToPithosFSPath(Path hadoopPath) {
		fsPathStr = hadoopPath.toString();

		fsPathStr = fsPathStr.substring(pithosFs.getScheme().toString()
				.concat("://").length());

		pathParts = fsPathStr.split("/");

		this.container = pathParts[0];
		this.object_path = fsPathStr.substring(getContainer().length() + 1);
	}

	public String getContainer() {
		return container;
	}

	public void setContainer(String container) {
		this.container = container;
	}

	public String getObjectPath() {
		return object_path;
	}

	public void setObjectPath(String object_path) {
		this.object_path = object_path;
	}

	public Path createFSPath() {
		fsPathStr = pithosFs.getScheme().concat("://").concat(getContainer())
				.concat("/").concat(getObjectPath());

		this.pithosFSPath = new Path(fsPathStr);

		return getPithosFSPath();
	}

	public Path getPithosFSPath() {
		return pithosFSPath;
	}

	@Override
	public String toString(){
		return getPithosFSPath().toString();
	}
	
}