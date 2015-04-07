package gr.grnet.escience.fs.pithos;

import java.net.URI;
import java.net.URISyntaxException;

import org.apache.hadoop.fs.Path;

public class PithosPath extends Path {

	public PithosPath(String pathString) throws IllegalArgumentException,
			URISyntaxException {
		super(pathString);
	}

	public PithosPath(URI aUri) {
		super(aUri);
	}

	public PithosPath(String parent, String child) {
		super(parent, child);
		// TODO Auto-generated constructor stub
	}

	public PithosPath(Path parent, String child) {
		super(parent, child);
		// TODO Auto-generated constructor stub
	}

	public PithosPath(String parent, Path child) {
		super(parent, child);
		// TODO Auto-generated constructor stub
	}

	public PithosPath(Path parent, Path child) {
		super(parent, child);
		// TODO Auto-generated constructor stub
	}

	public PithosPath(String scheme, String authority, String path) {
		super(scheme, authority, path);
		// TODO Auto-generated constructor stub
	}

}
