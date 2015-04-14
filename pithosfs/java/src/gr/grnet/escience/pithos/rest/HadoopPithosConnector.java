package gr.grnet.escience.pithos.rest;

import gr.grnet.escience.fs.pithos.PithosBlock;
import gr.grnet.escience.fs.pithos.PithosFileType;
import gr.grnet.escience.fs.pithos.PithosInputStream;
import gr.grnet.escience.fs.pithos.PithosObject;
import gr.grnet.escience.fs.pithos.PithosSystemStore;
import gr.grnet.escience.pithos.restapi.PithosRESTAPI;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Collection;
import java.util.List;
import java.util.Map;

import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;

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

public class HadoopPithosConnector extends PithosRESTAPI implements
		PithosSystemStore {

	private static final long serialVersionUID = 1L;
	private PithosRequest request;
	private PithosResponse response;
	private File srcFile2bUploaded;
	private File tmpFile2bUploaded;
	private File destfile2bUploaded;
	private File pithosBlockAsFile = new File("block");
	private String fileExtension;
	private int fileExtensionPointer;
	private File block_data;
	private InputStream pithosFileInputStream;
	private FileInputStream fileInputStream;

	/********************************************************
	 * (PITHOS <--> HADOOP): ANSTRACT METHODS THAT SUPPORT THE INTRERACTION
	 * BETWEEN PITHOS AND HADOOP
	 ********************************************************/
	/*****
	 * Constructor
	 */
	public HadoopPithosConnector(String pithosUrl, String pithosToken,
			String uuid) {
		// - implement aPithos RESTAPI instance
		super(pithosUrl, pithosToken, uuid);
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
	public byte[] serializeFile(File inputFile) {
		// - Convert File in bytes []
		byte[] block_data_bytes = new byte[(int) inputFile.length()];

		// - Perform the conversion
		try {
			// - Convert file into array of bytes
			fileInputStream = new FileInputStream(inputFile);
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
	public File deserializeFile(byte[] data) {
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

	/********************************************************
	 * (PITHOS --> HADOOP): GET / STREAM DATA FROM PITHOS
	 ********************************************************/
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
	public String getFileList(String pithos_container) {
		// - Create Pithos request
		setPithosRequest(new PithosRequest());

		// - Create Response instance
		setPithosResponse(new PithosResponse());
		String response_data = "";
		// - Read meta-data and add the data on the Pithos Response
		try {
			// - Perform action by using Pithos REST API method
			response_data = list_container_objects(pithos_container,
					getPithosRequest().getRequestParameters(),
					getPithosRequest().getRequestHeaders());
			// - Return the response data as String
			return response_data;
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
	}

	@Override
	public File retrievePithosObject(String pithos_container,
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
	public long getPithosObjectSize(String pithos_container,
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
			return Long.parseLong(hashMapResp.getObjectSize());
		} catch (IOException e) {
			e.printStackTrace();
			return -1;
		}
	}

	@Override
	public PithosBlock retrievePithosBlock(String pithos_container,
			String object_location, String block_hash) {

		// - Get required info for the object and the block
		long object_total_size = getPithosObjectSize(pithos_container,
				object_location);
		long block_size = getPithosObjectBlockSize(pithos_container,
				object_location);
		int object_blocks_number = getPithosObjectBlocksNumber(
				pithos_container, object_location);

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
			block_data = (File) read_object_data(object_location,
					pithos_container,
					getPithosRequest().getRequestParameters(),
					getPithosRequest().getRequestHeaders());

			// - Return the created pithos object
			return new PithosBlock(block_hash, block_data.length(),
					serializeFile(block_data));
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
	public Collection<String> getPithosObjectBlockHashes(
			String pithos_container, String object_location) {
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
	public PithosBlock[] retrievePithosObjectBlocks(String pithos_container,
			String object_location) {
		// - Create local blocks Array
		PithosBlock[] blocks = null;

		// - Get the hashes of the blocks for the requested object
		Collection<String> block_hashes = getPithosObjectBlockHashes(
				pithos_container, object_location);

		// - Initialize the local blocks array
		blocks = new PithosBlock[block_hashes.size()];

		// - Get and store on array all the available blocks
		int block_counter = 0;
		for (String hash : block_hashes) {
			blocks[block_counter] = retrievePithosBlock(pithos_container,
					object_location, hash);

			// - Next block
			block_counter++;
		}

		return blocks;
	}

	@Override
	public File seekPithosBlock(String pithos_container, String target_object,
			String target_block_hash, long offsetIntoPithosBlock) {

		// - Get required info for the object and the block
		long object_total_size = getPithosObjectSize(pithos_container,
				target_object);
		long block_size = getPithosObjectBlockSize(pithos_container,
				target_object);

		// - Check if the requested offset if valid
//		if ((offsetIntoPithosBlock < object_total_size)
//				&& (offsetIntoPithosBlock < block_size)) {

			pithosBlockAsFile = pithosBlockInputStream(pithos_container,
					target_object, target_block_hash, offsetIntoPithosBlock);
			return pithosBlockAsFile;
//		} else {
//			return null;
//		}

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
	public long getPithosBlockDefaultSize(String pithos_container) {
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

		// - Request Parameters JSON Format
		if (format.equals(PithosResponseFormat.JSON)) {
			getPithosRequest().getRequestParameters().put("format", "json");
		} else {
			getPithosRequest().getRequestParameters().put("format", "xml");
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
	public FSDataInputStream pithosObjectInputStream(String pithos_container,
			String object_location) {

		// - Create input stream for pithos
		try {
			// - Return the input stream wrapped into a FSDataINputStream
			return new FSDataInputStream(new PithosInputStream(
					pithos_container, object_location));
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}

	}

	@Override
	public FSDataInputStream pithosBlockInputStream(String pithos_container,
			String object_location, String block_hash) {
		// - Create input stream for Pithos
		try {
			if (pithosFileInputStream != null) {
				pithosFileInputStream.close();
			}

			// - Get the file object from pithos
			PithosBlock pithosBlock = retrievePithosBlock(pithos_container,
					object_location, block_hash);

			// - Add File data to the input stream
			File pithosBlockData = deserializeFile(pithosBlock.getBlockData());

			// - Create File input stream
			pithosFileInputStream = new FileInputStream(pithosBlockData);

			// - Return the input stream wrapped into a FSDataINputStream
			// return pithosFileInputStream;
			return new FSDataInputStream(pithosFileInputStream);
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}

	}

	@Override
	public File pithosBlockInputStream(String pithos_container,
			String object_location, String block_hash,
			long offsetIntoPithosBlock) {

		// // - Get the file object from pithos
		// PithosBlock pithosBlock = retrievePithosBlock(pithos_container,
		// object_location, block_hash);

		// /////////////
		// - Get required info for the object and the block
		long object_total_size = getPithosObjectSize(pithos_container,
				object_location);
		long block_size = getPithosObjectBlockSize(pithos_container,
				object_location);
		int object_blocks_number = getPithosObjectBlocksNumber(
				pithos_container, object_location);

		Collection<String> object_block_hashes = getPithosObjectBlockHashes(
				pithos_container, object_location);

		// - Iterate on available hashes
		int block_location_pointer_counter = 1;
		for (String hash : object_block_hashes) {
			// - If the hash is the requested hash
			if (hash.equals(block_hash)) {
				break;
			}
			// - Move the pointer one step forward
			block_location_pointer_counter++;
		}

		System.out
				.println("Object pointer = " + block_location_pointer_counter);

		// - Find the bytes range of the current block
		long[] range = bytesRange(object_total_size, block_size,
				object_blocks_number, block_location_pointer_counter);

		System.out.println("RANGE [" + range[0] + "-" + range[1] + "]");

		// - Check if the requested offset is between the actual range of the
		// block
		if ((offsetIntoPithosBlock >= range[0])
				&& (offsetIntoPithosBlock < range[1])) {

			try {
				// - Get the block as file based on the requested offset
				setPithosRequest(new PithosRequest());

				// - Request Parameters
				// - JSON Format
				getPithosRequest().getRequestParameters().put("format", "json");

				// - Add requested parameter for the range
				// - If it is not requested the last block, the add specific
				// range
				getPithosRequest().getRequestHeaders().put("Range",
						"bytes=" + offsetIntoPithosBlock + "-" + range[1]);

				// - Get the chunk of the pithos object as a file
				block_data = (File) read_object_data(object_location,
						pithos_container, getPithosRequest()
								.getRequestParameters(), getPithosRequest()
								.getRequestHeaders());

				// -Return the actual data of after the block seek
				return block_data;
			} catch (IOException e) {
				e.printStackTrace();
				return null;
			}
		} else {
			System.err
					.println("The defined offset into seek Pithos Block is out of range...\n\t"
							+ "offset = "
							+ offsetIntoPithosBlock
							+ " | BlockRange["
							+ range[0]
							+ "-"
							+ range[1]
							+ "]");

			return null;
		}

	}

	@Override
	public void deletePithosObject(String pithos_container,
			String object_location) {
		// TODO Auto-generated method stub

	}

	@Override
	public void deletePithosBlock(String block_hash) {
		// TODO Auto-generated method stub

	}

	@Override
	public boolean pithosObjectExists(String pithos_container,
			String pithos_object_name) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public boolean pithosObjectBlockExists(String blockHash) {
		// TODO Auto-generated method stub
		return false;
	}

	/********************************************************
	 * (HADOOP --> PITHOS): POST/PUT STREAM DATA TO PITHOS
	 ********************************************************/
	@Override
	public String storePithosObject(String pithos_container,
			String object_name, PithosObject pithos_object) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public String storeFileToPithos(String pithos_container, String source_file) {
		// - Create Pithos request
		setPithosRequest(new PithosRequest());

		// - Header Parameters
		// - Format of the uploaded file
		getPithosRequest().getRequestHeaders()
				.put("Content-Type", "text/plain");

		try {
			// - Convert hadoop output file to java file that is compatible with
			// Pithos
			srcFile2bUploaded = new File(source_file);

			// - If there is successful renaming of the object into the required
			// name
			// - Post data and get the response
			return upload_file(srcFile2bUploaded, null, pithos_container,
					getPithosRequest().getRequestParameters(),
					getPithosRequest().getRequestHeaders());
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}

	}

	@Override
	public String storePithosBlock(String pithos_container,
			String target_object, PithosBlock pithos_block, File backup_file) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public String pithosFSDataOutputStream(String pithos_container,
			PithosFileType file_type, FSDataOutputStream fs_output_stream) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public String pithosOutputStream(String pithos_container, String file_name,
			PithosFileType file_type, byte[] data) {
		// - Create Pithos request
		setPithosRequest(new PithosRequest());

		// - Check the file type that is going to be uploaded
		if (file_type.equals(PithosFileType.BLOCK)) {
			// - TODO: Append block on object not write new object
			// - Header Parameters
			// - Format of the uploaded file
			getPithosRequest().getRequestHeaders().put("Content-Type",
					"application/octet-stream");

			return null;
		} else {
			// - Header Parameters
			// - Format of the uploaded file
			getPithosRequest().getRequestHeaders().put("Content-Type",
					"text/plain");

			try {
				// - Convert hadoop output bytes to java file that is compatible
				// with Pithos
				srcFile2bUploaded = deserializeFile(data);
				// - Get the extension of the hadoop output file
				fileExtensionPointer = srcFile2bUploaded.getAbsolutePath()
						.lastIndexOf(".") + 1;
				fileExtension = srcFile2bUploaded.getAbsolutePath().substring(
						fileExtensionPointer);

				// - Rename the hadoop output file and keep the extension as it
				// was exported by hadoop so as to be stored as unchanged file
				tmpFile2bUploaded = srcFile2bUploaded;

				destfile2bUploaded = new File(file_name.concat(".").concat(
						fileExtension));

				// - If there is successful renaming of the object into the
				// required
				// name
				if (tmpFile2bUploaded.renameTo(destfile2bUploaded)) {
					// - Post data and get the response
					return upload_file(destfile2bUploaded, null,
							pithos_container, getPithosRequest()
									.getRequestParameters(), getPithosRequest()
									.getRequestHeaders());
				} else {
					return null;
				}
			} catch (IOException e) {
				e.printStackTrace();
				return null;
			}
		}
	}

	@Override
	public String pithosFileOutputStream(String pithos_container,
			String object_name, File file) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public String pithosObjectOutputStream(String pithos_container,
			String object_name, PithosObject pithos_object) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public String pithosBlockOutputStream(String pithos_container,
			String block_hash, PithosBlock pithos_block) {
		// TODO Auto-generated method stub
		return null;
	}

}
