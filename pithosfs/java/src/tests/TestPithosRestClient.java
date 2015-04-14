package tests;

import gr.grnet.escience.commons.PithosSerializer;
import gr.grnet.escience.fs.pithos.PithosBlock;
import gr.grnet.escience.fs.pithos.PithosObject;
import gr.grnet.escience.pithos.rest.HadoopPithosConnector;
import gr.grnet.escience.pithos.rest.PithosResponse;
import gr.grnet.escience.pithos.rest.PithosResponseFormat;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.Collection;

import org.junit.Before;
import org.junit.Test;

public class TestPithosRestClient {
	private static final String PITHOS_STORAGE_SYSTEM_URL = "https://pithos.okeanos.grnet.gr/v1";
	private static final String UUID = "ec567bea-4fa2-433d-9935-261a0867ec60";
	private static final String TOKEN = "-0c6fk775-AEiOJiIW3FcBAy8jo7YCXsKVoNsp7j__8";
	private static final String PITHOS_CONTAINER = "";
	private static final String PITHOS_FILE_TO_DOWNLOAD = "tests/testBigNewObject.txt";
	private static final long OFFSET = 5194305;
	private static final String LOCAL_SOURCE_FILE_TO_UPLOAD = "testOutput.txt";
	private static final String PITHOS_OBJECT_NAME_TO_OUTPUTSTREAM = "tests/testBigNewObject.txt";
	private static final byte[] DUMMY_BLOCK_DATA = "TEST DATA".getBytes();
	private static PithosResponse pithosResponse;
	private static Collection<String> object_block_hashes;
	private static HadoopPithosConnector hdconnector;

	@Before
	public void createHdConnector() {
		// - CREATE HADOOP CONNECTOR INSTANCE
		hdconnector = new HadoopPithosConnector(PITHOS_STORAGE_SYSTEM_URL,
				TOKEN, UUID);
	}

	@Test
	public void testGet_Container_Info() {
		// - GET CONTAINER INFORMATION
		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("GET CONTAINER INFO");
		System.out
				.println("---------------------------------------------------------------------");
		pithosResponse = hdconnector.getContainerInfo(PITHOS_CONTAINER);
		System.out.println(pithosResponse.toString());
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testGet_Container_File_List() {
		// - GET THE FILE STATUS OF A SELECTED CONTAINER
		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("GET FILE LIST OF THE CONTAINER: [CONTAINER:<"
				+ PITHOS_CONTAINER + ">]");
		System.out
				.println("---------------------------------------------------------------------");
		System.out.println(hdconnector.getFileList(PITHOS_CONTAINER));
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testGet_Pithos_Object_Metadata() {
		// - GET METADATA OF A SPECIFIC OBJECT
		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("GET PITHOS OBJECT METADATA: [OBJECT:<"
				+ PITHOS_FILE_TO_DOWNLOAD + ">]");
		System.out
				.println("---------------------------------------------------------------------");
		pithosResponse = hdconnector.getPithosObjectMetaData(PITHOS_CONTAINER,
				PITHOS_FILE_TO_DOWNLOAD, PithosResponseFormat.JSON);
		System.out.println(pithosResponse.toString());
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testGet_Pithos_Object_Size() {
		// - GET OBJECT ACTUAL SIZE
		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("GET PITHOS OBJECT SIZE: [OBJECT:<"
				+ PITHOS_FILE_TO_DOWNLOAD + ">]");
		System.out
				.println("---------------------------------------------------------------------");
		long objectSize = hdconnector.getPithosObjectSize(PITHOS_CONTAINER,
				PITHOS_FILE_TO_DOWNLOAD);
		System.out.println("Requested Object Size: " + objectSize + " Bytes");
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testGet_Pithos_Object() {
		// - GET AND STORE THE ACTUAL OBJECT AS A FILE
		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("GET PITHOS ACTUAL OBJECT: [OBJECT:<"
				+ PITHOS_FILE_TO_DOWNLOAD
				+ ">] and STORE IT AS: <"
				+ PITHOS_FILE_TO_DOWNLOAD.substring(PITHOS_FILE_TO_DOWNLOAD
						.lastIndexOf("/") + 1) + ">");
		System.out
				.println("---------------------------------------------------------------------");
		File pithosActualObject = hdconnector.retrievePithosObject(
				PITHOS_CONTAINER, PITHOS_FILE_TO_DOWNLOAD, "data");
		System.out.println("File name: " + pithosActualObject.getName());
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testGet_Pithos_Object_Block_Hashes() {
		// - GET OBJECT HASHES
		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("GET PITHOS OBJECT BLOCK HASHES: [OBJECT:<"
				+ PITHOS_FILE_TO_DOWNLOAD + ">]");
		System.out
				.println("---------------------------------------------------------------------");
		object_block_hashes = hdconnector.getPithosObjectBlockHashes(
				PITHOS_CONTAINER, PITHOS_FILE_TO_DOWNLOAD);
		System.out.println("Block Hashes: " + object_block_hashes);
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testGet_Pithos_Object_Block_Default_Size() {
		// -GET BLOCK DEFAULT SIZE
		System.out
				.println("---------------------------------------------------------------------");
		System.out
				.println("GET PITHOS CONTAINER BLOCK DEFAULT SIZE: [CONTAINER:<pithos>]");
		System.out
				.println("---------------------------------------------------------------------");
		long blocksDefaultSize = hdconnector
				.getPithosBlockDefaultSize(PITHOS_CONTAINER);
		System.out.println("Container block defaut size: " + blocksDefaultSize
				+ " Bytes");
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testGet_Pithos_Object_Blocks_Number() {
		// - GET THE NUMBER OF THE BLOCKS THAT COMPRISE A PITHOS OBJECT
		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("GET PITHOS OBJECT #BLOCKS: [OBJECT:<"
				+ PITHOS_FILE_TO_DOWNLOAD + ">]");
		System.out
				.println("---------------------------------------------------------------------");
		int blocksNum = hdconnector.getPithosObjectBlocksNumber(
				PITHOS_CONTAINER, PITHOS_FILE_TO_DOWNLOAD);
		System.out.println("Object <" + PITHOS_FILE_TO_DOWNLOAD
				+ "> is comprised by: " + blocksNum + " Blocks");
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testGet_Pithos_Object_Block_Size() {
		// - GET OBJECT CURRENT BLOCK SIZE, IN CASE IT IS STORED WITH DIFFERENT
		// POLICIES THAT THE DEFAULTS
		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("GET PITHOS OBJECT BLOCK CURRENT SIZE: [OBJECT:<"
				+ PITHOS_FILE_TO_DOWNLOAD + ">]");
		System.out
				.println("---------------------------------------------------------------------");
		long blockSize = hdconnector.getPithosObjectBlockSize(PITHOS_CONTAINER,
				PITHOS_FILE_TO_DOWNLOAD);
		System.out.println("Current object - Block Size: " + blockSize
				+ " Bytes");
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testGet_Pithos_Object_Block() {
		// - GET OBJECT BLOCK BY HASH
		// - Get a block hash of the previously requested object
		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("GET PITHOS OBJECT ACTUAL BLOCK: [OBJECT:<"
				+ PITHOS_FILE_TO_DOWNLOAD + ">]");
		System.out
				.println("---------------------------------------------------------------------");
		String block_hash = "";
		int block_counter = 1;
		// - local loop to get the corresponding hash
		for (String hash : object_block_hashes) {
			// - Get the hash of the second block
			if (block_counter == 1) {
				block_hash = hash;
				break;
			}
			block_counter++;
		}

		// - Get the pithos block
		PithosBlock block = hdconnector.retrievePithosBlock(PITHOS_CONTAINER,
				PITHOS_FILE_TO_DOWNLOAD, block_hash);
		System.out.println(block.toString());
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testGet_Pithos_Object_Block_All() {
		// - GET OBJECT ALL BLOCKS
		System.out
				.println("---------------------------------------------------------------------");
		System.out
				.println("GET PITHOS OBJECT ALL ACTUAL BLOCKS WITH HASH & SIZE: [OBJECT:<"
						+ PITHOS_FILE_TO_DOWNLOAD + ">]");
		System.out
				.println("---------------------------------------------------------------------");
		PithosBlock[] blocks = hdconnector.retrievePithosObjectBlocks(
				PITHOS_CONTAINER, PITHOS_FILE_TO_DOWNLOAD);
		System.out.println("Object <" + PITHOS_FILE_TO_DOWNLOAD
				+ "> is comprised by '" + blocks.length + "' blocks:\n");
		// - Iterate on blocks
		for (int blockCounter = 0; blockCounter < blocks.length; blockCounter++) {
			System.out.println("\t- " + blocks[blockCounter].toString());
		}
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testRead_Pithos_Object() throws IOException {
		// - READ PITHOS OBJECT: ESSENTIALLY CREATES INPUTSTREAM FOR A PITHOS
		// OBJECT
		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("STREAM PITHOS OBJECT ACTUAL DATA: [OBJECT:<"
				+ PITHOS_FILE_TO_DOWNLOAD + ">]");
		System.out
				.println("---------------------------------------------------------------------");
		InputStream objectInputStream = hdconnector.pithosObjectInputStream(
				PITHOS_CONTAINER, PITHOS_FILE_TO_DOWNLOAD);
		System.out.println("Available data in object inputstream : "
				+ objectInputStream.available() + " Bytes");
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testRead_Pithos_Object_Block() throws IOException {
		// - READ PITHOS OBJECT BLOCK: ESSENTIALLY CREATES INPUTSTREAM FOR A
		// PITHOS OBJECT BLOCK REQUESTED BY IT'S HASH
		// - Get a block hash of the previously requested object
		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("STREAM PITHOS BLOCK ACTUAL DATA: [OBJECT:<"
				+ PITHOS_FILE_TO_DOWNLOAD + ">]");
		System.out
				.println("---------------------------------------------------------------------");
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
		InputStream objectBlockInputStream = hdconnector
				.pithosBlockInputStream("", PITHOS_FILE_TO_DOWNLOAD,
						r_block_hash);
		System.out.println("Available data in block inputstream : "
				+ objectBlockInputStream.available() + " Bytes");
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testPithos_Object_Block_InputStream_With_Offset()
			throws IOException {

		// - Local parameters
		String BLOCK_HASH = "c0283cf33ff641b3e0bf7c753351803b7bf0b2aa1de1f5e08a04d084cf783a14";

		// - READ PITHOS OBJECT BLOCK: ESSENTIALLY CREATES INPUTSTREAM FOR A
		// PITHOS OBJECT BLOCK REQUESTED BY IT'S HASH
		// - Get a block hash of the previously requested object
		System.out
				.println("---------------------------------------------------------------------");
		System.out
				.println("SEEK INTO PITHOS BLOCK DATA: [BLOCK PART OF OBJECT:<"
						+ PITHOS_FILE_TO_DOWNLOAD + ">]");
		System.out
				.println("---------------------------------------------------------------------");

		File objectBlockInputStream = hdconnector.pithosBlockInputStream("",
				PITHOS_FILE_TO_DOWNLOAD, BLOCK_HASH, OFFSET);
		System.out.println("Available data in block inputstream : "
				+ objectBlockInputStream.length() + " Bytes");
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testStore_File_To_Pithos() throws IOException {
		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("STORE ACTUAL FILE: <" + LOCAL_SOURCE_FILE_TO_UPLOAD
				+ "> TO PITHOS STORAGE SYSTEM AS OBJECT <"
				+ PITHOS_OBJECT_NAME_TO_OUTPUTSTREAM + ">");
		System.out
				.println("---------------------------------------------------------------------");
		String response = hdconnector.uploadFileToPithos("",
				LOCAL_SOURCE_FILE_TO_UPLOAD);
		System.out.println("RESPONSE FROM PITHOS: " + response);
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testStore_Object_To_Pithos() throws IOException {
		// - Create Pithos Object instance
		PithosObject pithosObj = new PithosObject(
				PITHOS_OBJECT_NAME_TO_OUTPUTSTREAM, null);

		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("STORE ACTUAL OBJECT: <" + pithosObj.getName()
				+ "> TO PITHOS STORAGE SYSTEM");
		System.out
				.println("---------------------------------------------------------------------");
		String response = hdconnector.storePithosObject(PITHOS_CONTAINER,
				pithosObj);
		System.out.println("RESPONSE FROM PITHOS: " + response);
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testAppend_Pithos_Small_Block() throws IOException {

		// - Local parameters
		String BLOCK_HASH = "65e71d1c0c2952a04baa9acfd2ba078a5134fb31aec6fc48dc96af0a5b9e53ba";

		// - Create Pithos Object instance
		PithosBlock pithosBlock = new PithosBlock(BLOCK_HASH,
				DUMMY_BLOCK_DATA.length, DUMMY_BLOCK_DATA);

		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("APPEND BLOCK: <" + pithosBlock.getBlockHash()
				+ "> TO PITHOS OBJECT <" + PITHOS_OBJECT_NAME_TO_OUTPUTSTREAM
				+ ">");
		System.out
				.println("---------------------------------------------------------------------");
		String response = hdconnector.appendPithosBlock(PITHOS_CONTAINER,
				PITHOS_OBJECT_NAME_TO_OUTPUTSTREAM, pithosBlock);
		System.out.println("RESPONSE FROM PITHOS: " + response);
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testAppend_Pithos_Big_Block() throws IOException {

		// - Local parameters
		String BLOCK_HASH = "1262c627a1349c1148276b85f5c27c6bd2c1c601d25677c22d84da1fa5a998c4";
		byte[] bigBlockData = PithosSerializer.serializeFile(new File(
				"bigBlock2.txt"));

		// - Create Pithos Object instance
		PithosBlock pithosBlock = new PithosBlock(BLOCK_HASH,
				DUMMY_BLOCK_DATA.length, bigBlockData);

		System.out
				.println("---------------------------------------------------------------------");
		System.out.println("APPEND BLOCK: <" + pithosBlock.getBlockHash()
				+ "> TO PITHOS OBJECT <" + PITHOS_OBJECT_NAME_TO_OUTPUTSTREAM
				+ ">");
		System.out
				.println("---------------------------------------------------------------------");
		String response = hdconnector.appendPithosBlock(PITHOS_CONTAINER,
				PITHOS_OBJECT_NAME_TO_OUTPUTSTREAM, pithosBlock);
		System.out.println("RESPONSE FROM PITHOS: " + response);
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	/**
	 * @param args
	 * @throws IOException
	 * 
	 */
	public static void main(String[] args) throws IOException {
		TestPithosRestClient client = new TestPithosRestClient();

		client.createHdConnector();
		// client.testGet_Container_Info();
		// client.testGet_Container_File_List();
		// client.testGet_Pithos_Object_Metadata();
		// client.testGet_Pithos_Object_Size();
		// client.testGet_Pithos_Object();
		client.testGet_Pithos_Object_Block_Hashes();
		// client.testGet_Pithos_Object_Block_Default_Size();
		// client.testGet_Pithos_Object_Blocks_Number();
		// client.testGet_Pithos_Object_Block();
		// client.testGet_Pithos_Object_Block_All();
		// client.testRead_Pithos_Object();
		// client.testRead_Pithos_Object_Block();
		// client.testPithos_Object_Block_InputStream_With_Offset();
		// client.testStore_File_To_Pithos();
		// client.testStore_Object_To_Pithos();
		// client.testAppend_Pithos_Block();
		// client.testAppend_Pithos_Big_Block();
	}

}
