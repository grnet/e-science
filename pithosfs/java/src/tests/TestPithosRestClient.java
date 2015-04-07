package tests;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.Collection;

import gr.grnet.escience.fs.pithos.PithosFileStatus;
import gr.grnet.escience.fs.pithos.PithosObjectBlock;
import gr.grnet.escience.fs.pithos.PithosPath;

import org.apache.hadoop.fs.Path;
import org.codehaus.jettison.json.JSONException;
import org.codehaus.jettison.json.JSONObject;
import org.junit.Before;
import org.junit.Test;
import gr.grnet.escience.pithos.rest.HadoopPithosConnector;
import gr.grnet.escience.pithos.rest.PithosResponse;
import gr.grnet.escience.pithos.rest.PithosResponseFormat;

public class TestPithosRestClient {
	static String filename;
	private static final String PITHOS_CONTAINER = "";
	private static String PITHOS_FILE = "uUSer";
	private static PithosResponse pithosResponse;
	private static String pithosListResponse;
	private static Collection<String> object_block_hashes;
	private static HadoopPithosConnector hdconnector;

	@Before
	public static void createHdConnector() {
		// - CREATE HADOOP CONNECTOR INSTANCE
		hdconnector = new HadoopPithosConnector("https://pithos.okeanos.grnet.gr/v1", "juUVEDtgTftG24r-JA4pAvaU9c-UB2353op42-D0REQ", "fc1bd1b1-9691-4142-b759-12a12a1e6fe3");
	}
	
//	@Test
//	public static void testgetContainerList() {
//		// - GET CONTAINER INFORMATION
//		System.out
//				.println("---------------------------------------------------------------------\n");
//		pithosListResponse = hdconnector.getContainerList(PITHOS_CONTAINER);
//		System.out.println(pithosListResponse);
//		System.out
//				.println("---------------------------------------------------------------------\n");
//	}

	@Test
	public static void testGet_Container_Info() {
		// - GET CONTAINER INFORMATION
		System.out
				.println("---------------------------------------------------------------------\n");
		pithosResponse = hdconnector.getContainerInfo(PITHOS_CONTAINER);
		System.out.println(pithosResponse);
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public static void testGet_Pithos_Object_Metadata() {
		// - GET METADATA OF A SPECIFIC OBJECT
		System.out
				.println("---------------------------------------------------------------------\n");
		pithosResponse = hdconnector.getPithosObjectMetaData(PITHOS_CONTAINER,
				PITHOS_FILE, PithosResponseFormat.JSON);
		System.out.println(pithosResponse.toString());
//		try {
//			JSONObject obj = new JSONObject(pithosResponse.toString());
//			String contentLength = obj.getJSONObject("pithosResponse").getString("Content-Length");
//			int left = contentLength.indexOf("[\"");
//			int right = contentLength.indexOf("\"]");
//			String objlength = contentLength.substring(left+2, right);
//			long length = Long.parseLong(objlength);
//			System.out.println(length);
//		} catch (JSONException e) {
//			// TODO Auto-generated catch block
//			e.printStackTrace();
//		}
		PithosResponse metadata = hdconnector.getPithosObjectMetaData(PITHOS_CONTAINER, PITHOS_FILE, PithosResponseFormat.JSON);
		try {
			System.out.println("metadata: " + metadata.toString());
			JSONObject obj = new JSONObject(metadata.toString());
			String objExist = obj.getJSONObject("pithosResponse").getString("null");
			boolean exist = true;
			if (objExist.contains("404")){
				System.out.println("File does not exist in Pithos FS.");
				exist = false;
			}		
			/*---------------------------------------------------------*/
			if (exist){		
				String getContentType = obj.getJSONObject("pithosResponse").getString("Content-Type");
				int left0 = getContentType.indexOf("[\"");
				int right0 = getContentType.indexOf("\"]");
				String isDirOrFile = getContentType.substring(left0+2, right0);
				boolean isDir = false;
				if (isDirOrFile.contains("directory")){
					isDir = true;
				}
				
				String lastMod = obj.getJSONObject("pithosResponse").getString("Last-Modified");
				int left1 = lastMod.indexOf("[\"");
				int right1 = lastMod.indexOf("\"]");
				String lastModified = lastMod.substring(left1+2, right1);
				System.out.println("modification date : " + lastModified);
				
				if (isDir){
					System.out.println("DIRECTORY");
				}else{
					System.out.println("NOT DIRECTORY");
					String contentLength = obj.getJSONObject("pithosResponse").getString("Content-Length");
					int left = contentLength.indexOf("[\"");
					int right = contentLength.indexOf("\"]");
					String objlength = contentLength.substring(left+2, right);
					long length = Long.parseLong(objlength);
					System.out.println("object length: " + length);
				}
			}
		}catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testGet_Pithos_Object_Size() {
		// - GET OBJECT ACTUAL SIZE
		System.out
				.println("---------------------------------------------------------------------\n");
		long objectSize = hdconnector.getPithosObjectSize(PITHOS_CONTAINER,
				PITHOS_FILE);
		System.out.println("Requested Object Size: " + objectSize + " Bytes");
		System.out
				.println("---------------------------------------------------------------------\n");
	}

//	@Test
//	public static void testGet_Pithos_Object() {
//		// - GET AND STORE THE ACTUAL OBJECT AS A FILE
//		System.out
//				.println("---------------------------------------------------------------------\n");
//		File pithosActualObject = hdconnector.getPithosObject(PITHOS_CONTAINER,
//				PITHOS_FILE, "data");
//		System.out.println("File name: " + pithosActualObject.getName());
//		System.out
//				.println("---------------------------------------------------------------------\n");
//	}

	@Test
	public void testGet_Pithos_Object_Block_Hashes() {
		// - GET OBJECT HASHES
		System.out
				.println("---------------------------------------------------------------------\n");
		object_block_hashes = hdconnector.getPithosObjectBlockHashes(
				PITHOS_CONTAINER, PITHOS_FILE);
		System.out.println("Block Hashes: " + object_block_hashes);
		System.out
				.println("---------------------------------------------------------------------\n");
	}

//	@Test
//	public void testGet_Pithos_Object_Block_Default_Size() {
//		// -GET BLOCK DEFAULT SIZE
//		System.out
//				.println("---------------------------------------------------------------------\n");
//		long blocksDefaultSize = hdconnector
//				.getPithosObjectBlockDefaultSize(PITHOS_CONTAINER);
//		System.out.println("Container block defaut size: " + blocksDefaultSize
//				+ " Bytes");
//		System.out
//				.println("---------------------------------------------------------------------\n");
//	}

	@Test
	public void testGet_Pithos_Object_Blocks_Number() {
		// - GET THE NUMBER OF THE BLOCKS THAT COMPRISE A PITHOS OBJECT
		System.out
				.println("---------------------------------------------------------------------\n");
		int blocksNum = hdconnector.getPithosObjectBlocksNumber(
				PITHOS_CONTAINER, PITHOS_FILE);
		System.out.println("Object <" + PITHOS_FILE + "> is comprised by: "
				+ blocksNum + " Blocks");
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public static void testGet_Pithos_Object_Block_Size() {
		// - GET OBJECT CURRENT BLOCK SIZE, IN CASE IT IS STORED WITH DIFFERENT
		// POLICIES THAT THE DEFAULTS
		System.out
				.println("---------------------------------------------------------------------\n");
		long blockSize = hdconnector.getPithosObjectBlockSize(PITHOS_CONTAINER,
				PITHOS_FILE);
		System.out.println("Current object - Block Size: " + blockSize
				+ " Bytes");
		System.out
				.println("---------------------------------------------------------------------\n");
	}
//
//	@Test
//	public static void testGet_Pithos_Object_Block() {
//		// - GET OBJECT BLOCK BY HASH
//		// - Get a block hash of the previously requested object
//		System.out
//				.println("---------------------------------------------------------------------\n");
//		String block_hash = "";
//		int block_counter = 1;
//		// - local loop to get the corresponding hash
//		for (String hash : object_block_hashes) {
//			// - Get the hash of the second block
//			if (block_counter == 1) {
//				block_hash = hash;
//				break;
//			}
//			block_counter++;
//		}
//
//		// - Get the pithos block
//		PithosObjectBlock block = hdconnector.getPithosObjectBlock(
//				PITHOS_CONTAINER, PITHOS_FILE, block_hash);
//		System.out.println(block.toString());
//		System.out
//				.println("---------------------------------------------------------------------\n");
//	}
//
//	@Test
//	public void testGet_Pithos_Object_Block_All() {
//		// - GET OBJECT ALL BLOCKS
//		System.out
//				.println("---------------------------------------------------------------------\n");
//		PithosObjectBlock[] blocks = hdconnector.getPithosObjectBlockAll(
//				PITHOS_CONTAINER, PITHOS_FILE);
//		System.out.println("Object <" + PITHOS_FILE + "> is comprised by '"
//				+ blocks.length + "' blocks:\n");
//		// - Iterate on blocks
//		for (int blockCounter = 0; blockCounter < blocks.length; blockCounter++) {
//			System.out.println("\t- " + blocks[blockCounter].toString());
//		}
//		System.out
//				.println("---------------------------------------------------------------------\n");
//	}

	@Test
//	public static void testRead_Pithos_Object() throws IOException {
//		// - READ PITHOS OBJECT: ESSENTIALLY CREATES INPUTSTREAM FOR A PITHOS
		// OBJECT
//		System.out
//				.println("---------------------------------------------------------------------\n");
//		InputStream objectInputStream = hdconnector.readPithosObject(
//				PITHOS_CONTAINER, PITHOS_FILE);
//		System.out.println("Available data in object inputstream : "
//				+ objectInputStream.available() + " Bytes");
//		System.out
//				.println("---------------------------------------------------------------------\n");
//	}
//
//	@Test
	public void testRead_Pithos_Object_Block() throws IOException {
		// - READ PITHOS OBJECT BLOCK: ESSENTIALLY CREATES INPUTSTREAM FOR A
		// PITHOS OBJECT BLOCK REQUESTED BY IT'S HASH
		// - Get a block hash of the previously requested object
		System.out
				.println("---------------------------------------------------------------------\n");
		String r_block_hash = "";
		int r_block_counter = 1;
		// - local loop to get the corresponding hash
		for (String hash : object_block_hashes) {
			// - Get the hash of the second block
			if (r_block_counter == 1) {
				r_block_hash = hash;
				break;
			}
			r_block_counter++;
		}
//		InputStream objectBlockInputStream = hdconnector.readPithosObjectBlock(
//				"", PITHOS_FILE, r_block_hash);
//		System.out.println("Available data in block inputstream : "
//				+ objectBlockInputStream.available() + " Bytes");
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	/**
	 * @param args
	 * @throws IOException
	 * 
	 */
	public static void main(String[] args) throws IOException {
		// TODO: call the required method from above, so as to execute it	
		createHdConnector();
		//testRead_Pithos_Object();
		//testGet_Pithos_Object();
		//testgetContainerList();
		//testGet_Pithos_Object_Metadata();
//		Path f = new Path("pithos://pithos/folder/subfolder/pithosFile2.txt");
		
		PithosPath pithosPath;
		String pathToString;
		String[] filesList;
		
		Path f = new Path("pithos://pithos/folder/subfolder");
		pithosPath = new PithosPath(f);
		pathToString = pithosPath.toString();

		pathToString = pathToString.substring("pithos".concat("://").length());

		filesList = pathToString.split("/");
		filename = filesList[filesList.length - 1];
		int count = 2;
		while (!filesList[filesList.length-count].equals(pithosPath.getContainer())){
			filename = filesList[filesList.length-count]+"/"+filename;
			System.out.println("filename: " + filename);
			count ++;
		}
		
		String files[] = hdconnector.getFileList(pithosPath.getContainer()).split("\\r?\\n");
		// - Iterate on available files in the container
		for (int i = 0; i < files.length; i++) {
			String file = files[i].substring(files[i].lastIndexOf("/")+1);
			files[i] = files[i].substring(0, (files[i].length() - file.length()));
			if ((filename + "/").equals(files[i])) {
				Path path = new Path("pithos://"+pithosPath.getContainer()+"/"+filename + "/" + file);
				System.out.println("PATH!!:  " + path);
			}
			
//			String lsPathSplit[] = files[i].split("/");
//			for (int j=0; j<lsPathSplit.length;j++){
//				System.out.println("pathsplit: "+lsPathSplit[j]);
//				if (filename.equals(lsPathSplit[j])){
//					String containedFiles;
//					try {						
//						if (j+2 >= lsPathSplit.length) {
//							continue;
//						}
//						containedFiles = lsPathSplit[j] + "/" + lsPathSplit[j+1];	
//						System.out.println("confil: " + containedFiles);
//					} catch (Exception ArrayIndexOutOfBoundsException) {
//						continue;
//					}
//					Path path = new Path("pithos://"+pithosPath.getContainer()+"/"+containedFiles);
//					System.out.println("PATH!!:  " + path);
//				}
//			}
		}// end for
		
		
//			String pathStr = f.toString();
//			pathStr = pathStr.substring(pathStr.lastIndexOf(pathStr) + 9);
//			String pathSplit[] = pathStr.split("/");
//			String container = pathSplit[0];
//			String conList = hdconnector.getFileList(container);
//			
//			String targetFolder = pathSplit[pathSplit.length-1];
//			pathStr = pathStr.substring(pathStr.lastIndexOf(pathStr) + 9);
//			String files[] = conList.split("\\r?\\n");
//			for (int i = 0; i < files.length; i++) {
//				String lsPathSplit[] = files[i].split("/");
//				for (int j=0; j<lsPathSplit.length;j++){
//					if (targetFolder.equals(lsPathSplit[j])){
//						String containedFiles;
//						try {						
//							if (j+2 < lsPathSplit.length) {
//								continue;
//							}
//							containedFiles = lsPathSplit[j+1];	
//							Path path = new Path("folder/"+containedFiles);
//							System.out.println("PATH!!:  " + path);
//							PITHOS_FILE = "pithos/";
//							testGet_Pithos_Object_Metadata();
//						} catch (Exception ArrayIndexOutOfBoundsException) {
//							continue;
//						}
//					}
//				}
			
//			if (files[i] == pathSplit[i]) {
////			if (files[i] == ) {
//				Path path = new Path("pithos://"+container+"/"+files[i]);
//				System.out.println("PATH!!:  " + path);
//			}
		}
//		String pathSplit[] = pathStr.split("/");
//		String container = pathSplit[0];
		//System.out.println("Container: " + container);
//		String filename = f.toString().substring(
//				f.toString().lastIndexOf('/') + 1, f.toString().length());
	//		String filename = pathSplit[pathSplit.length-1];
	//		int count = 2;
	//		while (pathSplit[pathSplit.length-count] != container){
	//			filename = pathSplit[pathSplit.length-count]+"/"+filename;
	//			count ++;
	//		}
	//		System.out.println(filename);

//		PithosResponse metadata = hdconnector.getPithosObjectMetaData(container,
//				filename, PithosResponseFormat.JSON);
//		System.out.println(metadata);
		
//		String conList = hdconnector.getContainerList(container);
//		System.out.println(conList);
//		String folder = f.toString().substring(f.toString().lastIndexOf('/') + 1,
//				f.toString().length());
//		System.out.println("Folder: " + folder);
//		
//		String files[] = conList.split("\\r?\\n");
//		for (int i=0; i < files.length; i++){
//			int prevIndex = files[i].lastIndexOf('/', files[i].length() - 1);
//			String dir = files[i].substring(prevIndex + 1);
//			System.out.println("\nDIR: " + dir);
//			if (folder.equals(dir)){
//				String Index = f.toString().substring(f.toString().lastIndexOf('/') + 1,
//					f.toString().length());
//				System.out.println("Subfolds: "+Index);
//			}
//		}
////		System.out.println("Container List: \n" + conList);
////		String filename = arg0.toString().substring(arg0.toString().lastIndexOf('/') + 1,
////				arg0.toString().length());
////		System.out.println(filename);
////		if (conList.contains(filename)){
////			System.out.println("exists");
////		}else{
////			System.out.println("does not exist");
////		}
//	}

}
