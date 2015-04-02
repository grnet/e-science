package org.orka.hadoop.pithos.rest;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Collection;
import java.util.List;
import java.util.Map;

import org.apache.hadoop.fs.pithos.PithosObjectBlock;
import org.grnet.client.PithosRESTAPI;
import org.orka.hadoop.commons.Configurator;
import org.orka.hadoop.commons.Settings;

import com.google.gson.Gson;

/***
 * This class extends Pithos REST API that is implemented by grnet and supports
 * the implementation of particular methods for the interaction between hadoop
 * and Pithos Storage System.
 * 
 * {@link:
 * https://www.synnefo.org/docs/synnefo/latest/object-api-guide.html#object
 * -level}
 * 
 * @author dkelaidonis
 * @version 0.1
 * @since March, 2015
 */

public class HadoopPithosRestConnector extends PithosRESTAPI implements
		PithosRestIF {

	private static final long serialVersionUID = 1L;
	private static final String CONFIGURATION_FILE = "hadoopPithosConfiguration.json";
	private static final Settings hadoopConfiguration = Configurator
			.load(CONFIGURATION_FILE);
	private PithosRequest request;
	private PithosResponse response;

	/*****
	 * Constructor
	 */
	public HadoopPithosRestConnector() {
		// - implement aPithos RESTAPI instance
		super(hadoopConfiguration.getPithosUser().get("url"),// pithos auth-url
				hadoopConfiguration.getPithosUser().get("token"),// user-token
				hadoopConfiguration.getPithosUser().get("username"));// username

	}

	/***
	 * Pithos request
	 */
	private PithosRequest getPithosRequest() {
		return request;
	}

	private void setPithosRequest(PithosRequest request) {
		this.request = request;
	}

	/***
	 * Pithos response
	 */
	private PithosResponse getPithosResponse() {
		return response;
	}

	private void setPithosResponse(PithosResponse response) {
		this.response = response;
	}

	/**
	 * Manage Blocks
	 */
	private long[] bytesRange(long object_total_size, long block_size,
			int blocks_number, int block_pointer) {
		// - Initialize a long array that will keep 2 values; one for the start
		// of the range and one for the stop of the range of the bytes
		long[] range = { 0, 0 };
		// - Create
		long current_size = 0;

		// - Check if there are more than one blocks
		if (blocks_number > 1) {
			// - if the requested block is the first one
			if (block_pointer == 1) {
				// - Get range start
				range[0] = current_size;
				// - Get range stop
				range[1] = block_size;
			}
			// - if the requested block is the first one
			else if (block_pointer == blocks_number) {
				int previous_blocks = blocks_number - 1;
				long previous_size = block_size * previous_blocks;
				long last_block_size = object_total_size - previous_size;
				// - Get range start
				range[0] = (object_total_size - last_block_size) + 1;

				// - Get range stop
				range[1] = object_total_size;

			} else {
				// - Any intermediate block
				for (int i = 1; i <= blocks_number; i++) {
					// - if the current block is the requested one
					if (i == block_pointer) {
						// - Get range start
						range[0] = current_size;

						// - Get range stop
						range[1] = range[0] + block_size;

						// - stop the loop
						break;
					}

					current_size = (current_size + block_size) + 1;
				}
			}
		} else {
			// - Get range start
			range[0] = 0;
			// - Get range stop
			range[1] = object_total_size;
		}

		// - Return the table
		return range;
	}

	/**
	 * Serialize a file into bytes array
	 * 
	 * @param inputFile
	 *            : tha file that should be serialized into bytes array
	 * @return a File as bytes []
	 */
	private byte[] serializeFile(File inputFile) {
		// - Convert File in bytes []
		byte[] block_data_bytes = new byte[(int) inputFile.length()];

		// - Perform the conversion
		try {
			// - Convert file into array of bytes
			FileInputStream fileInputStream = new FileInputStream(inputFile);
			fileInputStream.read(block_data_bytes);
			fileInputStream.close();

			// - return the bytes array
			return block_data_bytes;
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}

	/**
	 * Deserialize a byte array into File
	 * 
	 * @param data
	 *            the byte array that should be desirialized int File
	 * @return return a File that actually constitutes the bytes that were
	 *         deserialized
	 */
	private File deserializeFile(byte[] data) {
		// convert array of bytes into file
		FileOutputStream fileOuputStream;
		try {
			// - Create file
			File block = new File("block");
			// - Create output stream with data to the file
			fileOuputStream = new FileOutputStream(block);
			fileOuputStream.write(data);
			fileOuputStream.close();
			// - return the file
			return block;
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
	}

	@Override
	public PithosResponse getContainerInfo(String pithos_container) {
		// - Create Pithos request
		setPithosRequest(new PithosRequest());

		// - Create Response instance
		setPithosResponse(new PithosResponse());

		// - Read meta-data and add the data on the Pithos Response
		try {
			// - If container argument is empty the initialize it with the
			// default value
			if (pithos_container.equals("")) {
				pithos_container = "pithos";
			}

			// - Perform action by using Pithos REST API method
			Map<String, List<String>> response_data = retrieve_container_info(
					pithos_container,
					getPithosRequest().getRequestParameters(),
					getPithosRequest().getRequestHeaders());

			// - Add data from pithos response on the corresponding java object
			getPithosResponse().setResponseData(response_data);

		} catch (IOException e) {
			e.printStackTrace();
		}

		// - Return the response data as String
		return getPithosResponse();
	}

	@Override
	public void createPithosObject(String pithos_container,
			String source_file, String pithos_object_location) {
		// TODO Auto-generated method stub

	}

	@Override
	public void uploadPithosObject(String pithos_container,
			String source_file, String destination_file) {
		// TODO Auto-generated method stub

	}

	@Override
	public File getPithosObject(String pithos_container,
			String object_location, String destination_file) {
		// - Create Pithos request
		setPithosRequest(new PithosRequest());

		// - Request Parameters
		// - JSON Format
		getPithosRequest().getRequestParameters().put("format", "json");

		// - Read data object
		try {

			return (File) read_object_data(object_location, pithos_container,
					getPithosRequest().getRequestParameters(),
					getPithosRequest().getRequestHeaders());
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
	}

	@Override
	public long getPithosObjectSize(String pithos_container, String object_location) {
		// - Create Pithos request
		setPithosRequest(new PithosRequest());

		// - Request Parameters
		// - JSON Format
		getPithosRequest().getRequestParameters().put("format", "json");
		getPithosRequest().getRequestParameters().put("hashmap", "True");

		// - Read data object
		try {
			// - Get response data in json format
			String json = (String) read_object_data(object_location,
					pithos_container,
					getPithosRequest().getRequestParameters(),
					getPithosRequest().getRequestHeaders());

			// -Serialize json response into Java object PithosResponseHashmap
			PithosResponseHashmap hashMapResp = (new Gson()).fromJson(json,
					PithosResponseHashmap.class);

			// - Return the required value
			return Long.parseLong(hashMapResp.getObjectSize());
		} catch (IOException e) {
			e.printStackTrace();
			return -1;
		}
	}

	@Override
	public PithosObjectBlock getPithosObjectBlock(String pithos_container,
			String object_location, String block_hash) {

		// - Get required info for the object and the block
		long object_total_size = getPithosObjectSize(pithos_container,
				object_location);
		long block_size = getPithosObjectBlockSize(pithos_container, object_location);
		int object_blocks_number = getPithosObjectBlocksNumber(pithos_container,
				object_location);

		Collection<String> object_block_hashes = getPithosObjectBlockHashes(
				pithos_container, object_location);

		// - Iterate on available hashes
		int block_location_pointer_counter = 1;
		int block_location_pointer = 0;
		for (String hash : object_block_hashes) {
			// - If the hash is the requested hash
			if (hash.equals(block_hash)) {
				// - Get the location of the block
				block_location_pointer = block_location_pointer_counter;
				break;
			}
			// - Move the pointer one step forward
			block_location_pointer_counter++;
		}

		// - Get the Range of the byte for the requested block
		long[] block_bytes_range = bytesRange(object_total_size, block_size,
				object_blocks_number, block_location_pointer);

		// - Create byte array for the object
		// - Create Pithos request
		setPithosRequest(new PithosRequest());

		// - Request Parameters
		// - JSON Format
		getPithosRequest().getRequestParameters().put("format", "json");
		// - Add requested parameter for the range
		// - If it is not requested the last block, the add specific range
		if (block_bytes_range[1] != object_total_size) {
			getPithosRequest().getRequestHeaders().put(
					"Range",
					"bytes=" + block_bytes_range[0] + "-"
							+ block_bytes_range[1]);
		} else {
			getPithosRequest().getRequestHeaders().put("Range",
					"bytes=" + block_bytes_range[0] + "-");
		}

		// - Read data object
		try {
			// - Get the chunk of the pithos object as a file
			File block_data = (File) read_object_data(object_location,
					pithos_container,
					getPithosRequest().getRequestParameters(),
					getPithosRequest().getRequestHeaders());

			// - Return the created pithos object
			return (new PithosObjectBlock(block_hash, block_data.length(),
					serializeFile(block_data)));
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
	}

	@Override
	public int getPithosObjectBlocksNumber(String pithos_container,
			String object_location) {

		// - Create Pithos request
		setPithosRequest(new PithosRequest());

		// - Request Parameters
		// - JSON Format
		getPithosRequest().getRequestParameters().put("format", "json");
		getPithosRequest().getRequestParameters().put("hashmap", "True");

		// - Read data object
		try {
			// - Get response data in json format
			String json = (String) read_object_data(object_location,
					pithos_container,
					getPithosRequest().getRequestParameters(),
					getPithosRequest().getRequestHeaders());
			// -Serialize json response into Java object PithosResponseHashmap
			PithosResponseHashmap hashMapResp = (new Gson()).fromJson(json,
					PithosResponseHashmap.class);
			// - Return the required value
			return hashMapResp.getBlockHashes().size();
		} catch (IOException e) {
			e.printStackTrace();
			return -1;
		}

	}

	@Override
	public Collection<String> getPithosObjectBlockHashes(String pithos_container,
			String object_location) {
		// - Create Pithos request
		setPithosRequest(new PithosRequest());

		// - Request Parameters
		// - JSON Format
		getPithosRequest().getRequestParameters().put("format", "json");
		getPithosRequest().getRequestParameters().put("hashmap", "True");

		// - Read data object
		try {
			// - Get response data in json format
			String json = (String) read_object_data(object_location,
					pithos_container,
					getPithosRequest().getRequestParameters(),
					getPithosRequest().getRequestHeaders());
			// -Serialize json response into Java object PithosResponseHashmap
			PithosResponseHashmap hashMapResp = (new Gson()).fromJson(json,
					PithosResponseHashmap.class);
			// - Return the required value
			return hashMapResp.getBlockHashes();
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
	}

	@Override
	public PithosObjectBlock[] getPithosObjectBlockAll(
			String pithos_container, String object_location) {
		// - Create local blocks Array
		PithosObjectBlock[] blocks = null;

		// - Get the hashes of the blocks for the requested object
		Collection<String> block_hashes = getPithosObjectBlockHashes(
				pithos_container, object_location);

		// - Initialize the local blocks array
		blocks = new PithosObjectBlock[block_hashes.size()];

		// - Get and store on array all the available blocks
		int block_counter = 0;
		for (String hash : block_hashes) {
			blocks[block_counter] = getPithosObjectBlock(pithos_container,
					object_location, hash);

			// - Next block
			block_counter++;
		}

		return blocks;
	}

	@Override
	public long getPithosObjectBlockSize(String pithos_container,
			String object_location) {

		// - Create Pithos request
		setPithosRequest(new PithosRequest());

		// - Request Parameters
		// - JSON Format
		getPithosRequest().getRequestParameters().put("format", "json");
		getPithosRequest().getRequestParameters().put("hashmap", "True");

		// - Read data object
		try {
			// - Get response data in json format
			String json = (String) read_object_data(object_location,
					pithos_container,
					getPithosRequest().getRequestParameters(),
					getPithosRequest().getRequestHeaders());

			// -Serialize json response into Java object PithosResponseHashmap
			PithosResponseHashmap hashMapResp = (new Gson()).fromJson(json,
					PithosResponseHashmap.class);

			// - Return the required value
			return Long.parseLong(hashMapResp.getBlockSize());
		} catch (IOException e) {
			e.printStackTrace();
			return -1;
		}

	}

	@Override
	public long getPithosObjectBlockDefaultSize(String pithos_container) {
		// - Create response object
		PithosResponse resp = (new Gson()).fromJson(
				(new Gson()).toJson(getContainerInfo(pithos_container)),
				PithosResponse.class);

		// - Return the value of the block size
		return Long.parseLong(resp.getResponseData()
				.get("X-Container-Block-Size").get(0));

	}

	@Override
	public PithosResponse getPithosObjectMetaData(String pithos_container,
			String object_location, PithosResponseFormat format) {
		// - Create Pithos request
		setPithosRequest(new PithosRequest());

		// - Request Parameters
		// JSON Format
		if (format.equals(PithosResponseFormat.JSON)) {
			getPithosRequest().getRequestParameters().put("format", "json");
		} else {
			// TODO: for others supported formats such as XML
		}
		// - Get the actual object
		getPithosRequest().getRequestParameters().put("hashmap", "True");

		// - Create Response instance
		setPithosResponse(new PithosResponse());

		// - Read meta-data and add the data on the Pithos Response
		try {
			// - Perform action by using Pithos REST API method
			Map<String, List<String>> response_data = retrieve_object_metadata(
					object_location, pithos_container, getPithosRequest()
							.getRequestParameters(), getPithosRequest()
							.getRequestHeaders());

			// - Add data from pithos response on the corresponding java object
			getPithosResponse().setResponseData(response_data);

		} catch (IOException e) {
			e.printStackTrace();
		}

		// - Return Pithos Response object as the result
		return getPithosResponse();
	}

	@Override
	public InputStream readPithosObject(String pithos_container,
			String object_location) {
		// - Get the file object from pithos
		File pithosObject = getPithosObject(pithos_container,
				object_location, null);

		// - Create input stream for pithos
		try {
			// - Add File data to the input stream
			InputStream pithosFileInputStream = new FileInputStream(
					pithosObject);

			// - Return the input stream wrapped into a FSDataINputStream
			return pithosFileInputStream;
		} catch (FileNotFoundException e) {
			e.printStackTrace();
			return null;
		}

	}

	@Override
	public InputStream readPithosObjectBlock(String pithos_container,
			String object_location, String block_hash) {

		// - Get the file object from pithos
		PithosObjectBlock pithosBlock = getPithosObjectBlock(
				pithos_container, object_location, block_hash);

		// - Create input stream for pithos
		try {
			// - Add File data to the input stream
			File pithosBlockData = deserializeFile(pithosBlock.getBlockData());
			InputStream pithosFileInputStream = new FileInputStream(
					pithosBlockData);

			// - Return the input stream wrapped into a FSDataINputStream
			return pithosFileInputStream;
		} catch (FileNotFoundException e) {
			e.printStackTrace();
			return null;
		}

	}

	@Override
	public void deletePithosObject(String pithos_container,
			String object_location) {
		// TODO Auto-generated method stub

	}

	@Override
	public void mmkdirOnPithos(String pithos_container, String directory_name) {
		// TODO Auto-generated method stub

	}

}
