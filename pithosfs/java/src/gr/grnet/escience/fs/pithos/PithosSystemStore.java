package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.pithos.rest.PithosResponse;
import gr.grnet.escience.pithos.rest.PithosResponseFormat;

import java.io.File;
import java.util.Collection;

import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;

public interface PithosSystemStore {

	/**************************
	 * PITHOS CONTAINER LEVEL
	 **************************/
	public PithosResponse getContainerInfo(String pithos_container);

	public String getFileList(String pithos_container);

	/**************************
	 * PITHOS OBJECT LEVEL
	 **************************/
	/***
	 * Downloads and stores on the defined destination location, the overall
	 * object from pithos, without the definition of particular chunk
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coresponds to 'Pithos'
	 * @param object_location
	 *            : the location of the object into the Pithos default container
	 * @param object_destination_location
	 *            : the location where the requested Pithos object will be
	 *            downloaded and stored
	 */
	public File retrievePithosObject(String pithos_container,
			String object_location, String destination_file);

	/**
	 * Get the total size of a Pithos object that is available into the selected
	 * container
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coresponds to 'Pithos'
	 * @param object_location
	 *            : the location of the object into the Pithos default container
	 * @return the total size in bytes of the requested Pithos Object
	 */
	public long getPithosObjectSize(String pithos_container,
			String object_location);

	/**
	 * Downloads and stores on the defined destination location, a chunk of the
	 * defined object from Pithos, without the definition of particular chunk
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coressponds to 'Pithos'
	 * @param target_object
	 *            : the object of which the block will be retrieved
	 * @param block_hash
	 *            : the hash code of the block that will be retrieved
	 */
	public PithosBlock retrievePithosBlock(String pithos_container,
			String target_object, String block_hash);

	/**
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos
	 * @param target_object
	 *            : the object on which the seek method will seek on its blocks
	 * @param target_block_hash
	 *            : the hash of the selected block
	 * @param offsetIntoPithosBlock
	 *            : the starting point of the range for the retrieved data
	 * @return a file that includes the data of the requested chunk og data
	 *         based on the defined offset
	 */
	public File seekPithosBlock(String pithos_container, String target_object,
			String target_block_hash, long offsetIntoPithosBlock);

	/**
	 * Get the hashes of all blocks that comprise the requested object
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param object_location
	 *            : the location of the object into the Pithos default container
	 * @return a collection of Strings that each String corresponds to hash code
	 *         of the available blocks
	 */
	public Collection<String> getPithosObjectBlockHashes(
			String pithos_container, String object_location);

	/**
	 * Downloads and stores on the defined destination location, a chunk of the
	 * defined object from Pithos, without the definition of particular chunk
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coresponds to 'Pithos'
	 * @param target_object
	 *            : the location of the object into the Pithos default container
	 *            that should be retrieved
	 */
	public PithosBlock[] retrievePithosObjectBlocks(String pithos_container,
			String target_object);

	/**
	 * Get the total number of the blocks that comprise the overal block
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coresponds to 'Pithos'
	 * @param object_location
	 *            : the location of the object into the Pithos default container
	 * @return: the total number of the blocks that comprise the Object
	 */
	public int getPithosObjectBlocksNumber(String pithos_container,
			String object_location);

	/**
	 * Get the current size of the requested object in bytes
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param object_location
	 *            : the object that its block size will be checked
	 */
	public long getPithosObjectBlockSize(String pithos_container,
			String object_location);

	/**
	 * Get the default object size in bytes that is defined for the specified
	 * container. The default block size is included in the Container info.
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 */
	public long getPithosBlockDefaultSize(String pithos_container);

	/***
	 * Method to get the meta-data that correspond to a Pithos object stored
	 * under the default ("Pithos")
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coresponds to 'Pithos'
	 * @param object_location
	 *            : the location of the requested object into Pithos storage
	 *            system
	 * @param format
	 *            : the format in which the object meta-data will be received
	 * @return a string that corresponds to the set of meta-data for the
	 *         requested object in the specified format (JSON or XML)
	 */
	public PithosResponse getPithosObjectMetaData(String pithos_container,
			String object_location, PithosResponseFormat format);

	/**
	 * Read the data of the object that is available in Pithos, by using an
	 * InputStream, without the need to store the data on the local system where
	 * the Hadoop ecosystem is running. Essentially it feeds directly Hadoop
	 * with data from the object
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coresponds to 'Pithos'
	 * @param object_location
	 *            : the location of the object, that it is requested to be read,
	 *            in Pithos
	 */
	public FSDataInputStream pithosObjectInputStream(String pithos_container,
			String object_location);

	/**
	 * Read the data of an object chunk that is available in Pithos, by using an
	 * InputStream, without the need to store the data on the local system where
	 * the Hadoop ecosystem is running. Essentially it feeds directly Hadoop
	 * with data from the object
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param object_location
	 *            : the location of the object, that it is requested to be read,
	 *            in Pithos
	 * @param object_size
	 *            : the size in bytes of the object chunk that will be
	 *            downloaded and stored on the destination
	 */
	public FSDataInputStream pithosBlockInputStream(String pithos_container,
			String object_location, String block_hash);

	/**
	 * Delete the defined object from Pithos container
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param object_location
	 *            : the location of the object in Pithos
	 */
	public void deletePithosObject(String pithos_container,
			String object_location);

	/**
	 * Delete a block on Pithos storage system, by using its unique hash code
	 * 
	 * @param block_hash
	 *            : the block hash that is going to be deleted
	 */
	public void deletePithosBlock(String block_hash);

	/**
	 * Uploads a file, from the local to the specified Pithos location, as
	 * Pithos Object into the default container. The difference with the
	 * 'createObjectToPithos' methods, refers to the fact that the current
	 * method creates a direct Outputstream from local to Pithos
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param object_name
	 *            : the name of the object that will be created on Pithos system
	 *            Store
	 * @param pithos_object
	 *            : the Pithos Object structured class object that packs the
	 *            data into Pithos object structure and it will be stored on
	 *            Pithos storage systme
	 */
	public String storePithosObject(String pithos_container,
			String object_name, PithosObject pithos_object);

	/**
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param target_object
	 *            : the name of the object on which the block will be appended
	 * @param pithos_block
	 *            : the actual Pithos Block that will be stored on Pithos
	 *            storage system
	 * @param backup_file
	 *            : the temporary file storing the block data to be streamed
	 * @return
	 */
	public String storePithosBlock(String pithos_container,
			String target_object, PithosBlock pithos_block, File backup_file);

	/**
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param source_file
	 *            : the absolute path of the file that should be uploaded/stored
	 *            to pithos storage system
	 */
	public String storeFileToPithos(String pithos_container, String source_file);

	/**
	 * Stream primitive data as bytes to Pithos storage system. It should be
	 * identified the type of the data that is going to be uploaded to Pithos,
	 * so as the outputstream to be configured appropriately.
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param file_name
	 *            : the name of the file that will be stored on Pithos stoarage
	 *            system
	 * @param file_type
	 *            : one of the possible types of data that can be added on
	 *            Pithos storage system <i>(OBJECT, BLOCK, FILE)</i>
	 * @param data
	 * @return
	 */
	public String pithosOutputStream(String pithos_container, String file_name,
			PithosFileType file_type, byte[] data);

	/**
	 * THis method aims to simplify the bridging between Hadoop output data
	 * tubes and Pithos storage system, by giving the abillity to open and
	 * connect a direct FS data outputstream to the pithos storage system.
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param file_type
	 *            : one of the possible types of data that can be added on
	 *            Pithos storage system <i>(OBJECT, BLOCK, FILE)</i>
	 * @param fs_output_stream
	 *            : the hadoop output stream that essentially streams a specific
	 *            type of dtaa
	 * @return
	 */
	public String pithosFSDataOutputStream(String pithos_container,
			PithosFileType file_type, FSDataOutputStream fs_output_stream);

	/**
	 * This method gets as input the container of the Pithos storage system, the
	 * name of a Pithos Object instance and the actual object instance and send
	 * the data to Pithos by streaming them to Pithos
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param pithos_object
	 *            : a Pithos Object instance that stores the data of the object
	 *            that will be stored on Pithos storage system
	 * 
	 * @return: the response code that is returned by the execution of the
	 *          method
	 */
	public String pithosObjectOutputStream(String pithos_container,
			String object_name, PithosObject pithos_object);

	/**
	 * This method gets as input the container of the Pithos storage system, the
	 * hash code of an Object Block instance and the actual block instance and
	 * append the object to Pithos through an output streaming
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param block_hash
	 *            : the sha-X hash code of the generated object
	 * @param pithos_block
	 * 
	 * @return: the response code that is returned by the execution of the
	 *          method
	 */
	public String pithosBlockOutputStream(String pithos_container,
			String block_hash, PithosBlock pithos_block);

	/**
	 * This method gets as input the container of the Pithos storage system, the
	 * name of a file that will be storege on Pithos as a Pithos Object and send
	 * the data to Pithos by streaming them to Pithos
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param object_name
	 *            : a Pithos Object instance that stores the data of the object
	 *            that will be stored on Pithos storage system
	 * @param file
	 *            : the actual file that will be stored on pithos
	 * 
	 * @return the response code that is returned by the execution of the method
	 */
	public String pithosFileOutputStream(String pithos_container,
			String object_name, File file);

	/**
	 * 
	 * @param pithos_container
	 * @param pithos_object_name
	 * @return <b>true</b> if the object exists and <b>false</b> if not
	 */
	public boolean pithosObjectExists(String pithos_container,
			String pithos_object_name);

	/**
	 * This method search for existing blocks on Pithos storage system by using
	 * a given hash code by the user
	 * 
	 * @param blockHash
	 *            : the hash code of the requested block
	 * @return <b>true</b> if the block exists and <b>false</b> if not
	 */
	public boolean pithosObjectBlockExists(String blockHash);

}
