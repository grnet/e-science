package gr.grnet.escience.fs.pithos;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Constructor;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.EnumSet;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.AbstractFileSystem;
import org.apache.hadoop.fs.BlockLocation;
import org.apache.hadoop.fs.CreateFlag;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileAlreadyExistsException;
import org.apache.hadoop.fs.FileChecksum;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.FsServerDefaults;
import org.apache.hadoop.fs.FsStatus;
import org.apache.hadoop.fs.Options.ChecksumOpt;
import org.apache.hadoop.fs.ParentNotDirectoryException;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.UnresolvedLinkException;
import org.apache.hadoop.fs.UnsupportedFileSystemException;
import org.apache.hadoop.fs.permission.FsPermission;
import org.apache.hadoop.security.AccessControlException;
import org.apache.hadoop.util.Progressable;
import gr.grnet.escience.pithos.rest.HadoopPithosRestConnector;

public class PithosAbstractFileSystem extends AbstractFileSystem {

	public PithosAbstractFileSystem(URI uri, String supportedScheme,
			boolean authorityNeeded, int defaultPort) throws URISyntaxException {
		super(uri, supportedScheme, authorityNeeded, defaultPort);
		// TODO Auto-generated constructor stub
	}

	@Override
	public FSDataOutputStream createInternal(Path arg0,
			EnumSet<CreateFlag> arg1, FsPermission arg2, int arg3, short arg4,
			long arg5, Progressable arg6, ChecksumOpt arg7, boolean arg8)
			throws AccessControlException, FileAlreadyExistsException,
			FileNotFoundException, ParentNotDirectoryException,
			UnsupportedFileSystemException, UnresolvedLinkException,
			IOException {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public boolean delete(Path arg0, boolean arg1)
			throws AccessControlException, FileNotFoundException,
			UnresolvedLinkException, IOException {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public BlockLocation[] getFileBlockLocations(Path arg0, long arg1, long arg2)
			throws AccessControlException, FileNotFoundException,
			UnresolvedLinkException, IOException {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public FileChecksum getFileChecksum(Path arg0)
			throws AccessControlException, FileNotFoundException,
			UnresolvedLinkException, IOException {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public FileStatus getFileStatus(Path arg0) throws AccessControlException,
			FileNotFoundException, UnresolvedLinkException, IOException {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public FsStatus getFsStatus() throws AccessControlException,
			FileNotFoundException, IOException {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public FsServerDefaults getServerDefaults() throws IOException {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public int getUriDefaultPort() {
		// TODO Auto-generated method stub
		return 0;
	}
	
//	public static AbstractFileSystem createFileSystem(URI uri, Configuration conf) throws UnsupportedFileSystemException {
//
//	     Class<?> clazz = conf.getClass("fs.AbstractFileSystem." + uri.getScheme() + ".impl", null);
//	     if (clazz == null) {
//	    	 throw new UnsupportedFileSystemException(
//	    			 "No AbstractFileSystem for scheme: " + uri.getScheme());
//	     }
//	     return (AbstractFileSystem) newInstance(clazz, uri, conf);
//	}
//	
//	   /** 
//	   * Create an object for the given class and initialize it from conf.
//	   * @param theClass class of which an object is created
//	   * @param conf Configuration
//	   * @return a new object
//	   */
//	  @SuppressWarnings("unchecked")
//	  static <T> T newInstance(Class<T> theClass,
//	    URI uri, Configuration conf) {
//	    T result;
//	    try {
//	      Constructor<T> meth = (Constructor<T>) CONSTRUCTOR_CACHE.get(theClass);
//	      if (meth == null) {
//	        meth = theClass.getDeclaredConstructor(URI_CONFIG_ARGS);
//	        meth.setAccessible(true);
//	        CONSTRUCTOR_CACHE.put(theClass, meth);
//	      }
//	      result = meth.newInstance(uri, conf);
//	    } catch (Exception e) {
//	      throw new RuntimeException(e);
//	    }
//	    return result;
//	  }


	@Override
	public FileStatus[] listStatus(Path path) throws AccessControlException,
			FileNotFoundException, UnresolvedLinkException, IOException {
		System.out.println("list status: " + super.getUri() + " ...");
		Configuration conf = new Configuration();
		conf.set("fs.defaultFS", super.getUri().toString());
		conf.set("fs.AbstractFileSystem.pithos.impl", "gr.grnet.escience.fs.pithos.PithosAbstractFileSystem");
		conf.set("hadoop.job.ugi", "hduser");
		AbstractFileSystem afs = AbstractFileSystem.get(super.getUri(), conf);
		
		FileStatus[] status = afs.listStatus(path);
	    for(int i=0;i<status.length;i++){
	        System.out.println(status[i].getPath());
	    }
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public void mkdir(Path arg0, FsPermission arg1, boolean arg2)
			throws AccessControlException, FileAlreadyExistsException,
			FileNotFoundException, UnresolvedLinkException, IOException {
		// TODO Auto-generated method stub

	}

	@Override
	/**
	 * @param arg0: refers to the path on the file system
	 * @parma arg1: refers to the bufferSize of the input stream
	 */
	public FSDataInputStream open(Path path, int bufferSize)
			throws AccessControlException, FileNotFoundException,
			UnresolvedLinkException, IOException {
		System.out.println("open " + super.getUri());
		Configuration conf = new Configuration();
		conf.set("fs.defaultFS", super.getUri().toString());
		conf.set("fs.AbstractFileSystem.pithos.impl", "gr.grnet.escience.fs.pithos.PithosAbstractFileSystem");
		conf.set("hadoop.job.ugi", "hduser");
		AbstractFileSystem afs = AbstractFileSystem.get(super.getUri(), conf);
		
		FSDataInputStream fsdis = afs.open(path);
		
		//HadoopPithosRestConnector conn = new HadoopPithosRestConnector();
		String container = path.getParent().toString();		
		//FSDataInputStream fsdis = conn.readPithosObject(container, path.toString()); 
		//FSDataInputStream ffsdis = new FSDataInputStream(fsdis);
		// TODO
		return fsdis;
	}

	@Override
	public void renameInternal(Path arg0, Path arg1)
			throws AccessControlException, FileAlreadyExistsException,
			FileNotFoundException, ParentNotDirectoryException,
			UnresolvedLinkException, IOException {
		// TODO Auto-generated method stub

	}

	@Override
	public void setOwner(Path arg0, String arg1, String arg2)
			throws AccessControlException, FileNotFoundException,
			UnresolvedLinkException, IOException {
		// TODO Auto-generated method stub

	}

	@Override
	public void setPermission(Path arg0, FsPermission arg1)
			throws AccessControlException, FileNotFoundException,
			UnresolvedLinkException, IOException {
		// TODO Auto-generated method stub

	}

	@Override
	public boolean setReplication(Path arg0, short arg1)
			throws AccessControlException, FileNotFoundException,
			UnresolvedLinkException, IOException {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public void setTimes(Path arg0, long arg1, long arg2)
			throws AccessControlException, FileNotFoundException,
			UnresolvedLinkException, IOException {
		// TODO Auto-generated method stub

	}

	@Override
	public void setVerifyChecksum(boolean arg0) throws AccessControlException,
			IOException {
		// TODO Auto-generated method stub

	}

}
