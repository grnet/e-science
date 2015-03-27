package tests;

import gr.grnet.escience.fs.pithos.PithosObjectBlock;
import gr.grnet.hadoop.pithos.rest.HadoopPithosRestConnector;
import gr.grnet.hadoop.pithos.rest.PithosResponse;
import gr.grnet.hadoop.pithos.rest.PithosResponseFormat;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.Collection;

import org.junit.Before;
import org.junit.Test;

public class TestPithosRestClient {
	private static final String PITHOS_CONTAINER = "";
	private static final String PITHOS_FILE = "test/testdata.txt";
	private static PithosResponse pithosResponse;
	private static Collection<String> object_block_hashes;
	private static HadoopPithosRestConnector hdconnector;

	@Before
	public void createHdConnector() {
		// - CREATE HADOOP CONNECTOR INSTANCE
		hdconnector = new HadoopPithosRestConnector();
	}

	@Test
	public void testGet_Container_Info() {
		// - GET CONTAINER INFORMATION
		System.out
				.println("---------------------------------------------------------------------\n");
		pithosResponse = hdconnector.getContainerInfo(PITHOS_CONTAINER);
		System.out.println(pithosResponse.toString());
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testGet_Pithos_Object_Metadata() {
		// - GET METADATA OF A SPECIFIC OBJECT
		System.out
				.println("---------------------------------------------------------------------\n");
		pithosResponse = hdconnector.getPithosObjectMetaData(PITHOS_CONTAINER,
				PITHOS_FILE, PithosResponseFormat.JSON);
		System.out.println(pithosResponse.toString());
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

	@Test
	public void testGet_Pithos_Object() {
		// - GET AND STORE THE ACTUAL OBJECT AS A FILE
		System.out
				.println("---------------------------------------------------------------------\n");
		File pithosActualObject = hdconnector.getPithosObject(PITHOS_CONTAINER,
				PITHOS_FILE, "data");
		System.out.println("File name: " + pithosActualObject.getName());
		System.out
				.println("---------------------------------------------------------------------\n");
	}

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

	@Test
	public void testGet_Pithos_Object_Block_Default_Size() {
		// -GET BLOCK DEFAULT SIZE
		System.out
				.println("---------------------------------------------------------------------\n");
		long blocksDefaultSize = hdconnector
				.getPithosObjectBlockDefaultSize(PITHOS_CONTAINER);
		System.out.println("Container block defaut size: " + blocksDefaultSize
				+ " Bytes");
		System.out
				.println("---------------------------------------------------------------------\n");
	}

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
	public void testGet_Pithos_Object_Block_Size() {
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

	@Test
	public void testGet_Pithos_Object_Block() {
		// - GET OBJECT BLOCK BY HASH
		// - Get a block hash of the previously requested object
		System.out
				.println("---------------------------------------------------------------------\n");
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
		PithosObjectBlock block = hdconnector.getPithosObjectBlock(
				PITHOS_CONTAINER, PITHOS_FILE, block_hash);
		System.out.println(block.toString());
		System.out
				.println("---------------------------------------------------------------------\n");
	}

	@Test
	public void testGet_Pithos_Object_Block_All() {
		// - GET OBJECT ALL BLOCKS
		System.out
				.println("---------------------------------------------------------------------\n");
		PithosObjectBlock[] blocks = hdconnector.getPithosObjectBlockAll(
				PITHOS_CONTAINER, PITHOS_FILE);
		System.out.println("Object <" + PITHOS_FILE + "> is comprised by '"
				+ blocks.length + "' blocks:\n");
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
				.println("---------------------------------------------------------------------\n");
		InputStream objectInputStream = hdconnector.readPithosObject(
				PITHOS_CONTAINER, PITHOS_FILE);
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
		InputStream objectBlockInputStream = hdconnector.readPithosObjectBlock(
				"", PITHOS_FILE, r_block_hash);
		System.out.println("Available data in block inputstream : "
				+ objectBlockInputStream.available() + " Bytes");
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
	}

}
