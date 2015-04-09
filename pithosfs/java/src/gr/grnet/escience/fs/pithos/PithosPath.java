package gr.grnet.escience.fs.pithos;

import java.io.FileNotFoundException;

import org.apache.hadoop.fs.InvalidPathException;
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

	public PithosPath(Path hadoopPath) throws InvalidPathException, FileNotFoundException {
		this.pithosFSPath = hadoopPath;
		convertHadoopFSPathToPithosFSPath(getPithosFSPath());
	}

	public PithosPath(String pithos_container, String pithos_object_path) {
		this.container = pithos_container;
		this.object_path = pithos_object_path;
	}

	private void convertHadoopFSPathToPithosFSPath(Path hadoopPath) throws InvalidPathException, FileNotFoundException {
		fsPathStr = hadoopPath.toString();

		fsPathStr = fsPathStr.substring(pithosFs.getScheme().toString()
				.concat("://").length());

		pathParts = (fsPathStr + "/").split("/");
		
		System.out.println("EDWWWWW : " + pathParts[pathParts.length-1]);
		
		if (pithosFs.containerExistance(pathParts[0])) {
			this.container = pathParts[0];
			this.object_path = fsPathStr.substring(getContainer().length() + 1);
			System.out.println("TI FTXNM: " + this.object_path);
		} else {
			InvalidPathException ipe = new InvalidPathException(pathParts[0], "No such pithos:// container");
			throw ipe;
		}
		
//		// Can't override hadoop message
//		if (!pithosFs.fileExistance(container, object_path.replace("\"", ""))) {
//			FileNotFoundException fnfe = new FileNotFoundException("File does not exist in Pithos FS.");
//			throw fnfe;
//		}
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