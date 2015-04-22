package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.pithos.rest.PithosResponse;
import gr.grnet.escience.pithos.rest.PithosResponseFormat;

import java.io.File;
import java.io.IOException;
import java.util.Collection;

import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;

public interface PithosSystemStore {

	/**************************
	 * PITHOS CONTAINER LEVEL
	 **************************/
	/**
	 * 
	 * @param pithos_container
	 * @return Pithos response in JSON format that includes information about a
	 *         selected container on +Pithos as they are identified into the
	 *         specifications / API {@link https
	 *         ://www.synnefo.org/docs/synnefo/latest/object-api-guide.html}
	 */

	public PithosResponse getContainerInfo(String pithos_container);

	/**
	 * 
	 * @param pithos_container
	 * @return The list of available files into the selected container.
	 */
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
	 *            corresponds to 'Pithos'
	 * @param target_object
	 *            : the object of which the block will be retrieved
	 * @param block_hash
	 *            : the hash code of the block that will be retrieved
	 */
	public PithosBlock retrievePithosBlock(String pithos_container,
			String target_object, String block_hash);

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

	/**
	 * Get the hash algorithm used to compute the digest of blocks stored in
	 * container
	 * 
	 * 
	 * @param pithos_container
	 *            : the Pithos container queried
	 * @return : name of hash algorithm used
	 */
	public String getPithosContainerHashAlgorithm(String pithos_container);

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
	 * @param block_hash
	 *            : the hash code of the requested block
	 * @return The input stream of the block data as FSDataInputStream
	 */
	public FSDataInputStream pithosBlockInputStream(String pithos_container,
			String object_location, String block_hash);

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
	 * @param block_hash
	 *            : the hash code of the requested block
	 * @param offsetIntoPithosBlock
	 *            : the starting point of the range for the retrieved data
	 * @return The input stream of the block data as FSDataInputStream
	 */
	public File pithosBlockInputStream(String pithos_container,
			String object_location, String block_hash,
			long offsetIntoPithosBlock);

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
			PithosObject pithos_object);

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
	 * @return A string that actually is the response code and message that
	 *         identifies the result of the current process based on the
	 *         corresponding response codes as they are described into
	 *         {@link https
	 *         ://www.synnefo.org/docs/synnefo/latest/object-api-guide.html}
	 */
	public String storePithosBlock(String pithos_container,
			String target_object, PithosBlock pithos_block, File backup_file);

	/**
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param target_object
	 *            : the name of the object on which the block will be appended
	 * @param newPithosBlock
	 *            : the actual Pithos Block that will be appended to the target
	 *            object
	 * @return A string that actually is the response code and message that
	 *         identifies the result of the current process based on the
	 *         corresponding response codes as they are described into
	 *         {@link https
	 *         ://www.synnefo.org/docs/synnefo/latest/object-api-guide.html}
	 */
	public String appendPithosBlock(String pithos_container,
			String target_object, PithosBlock newPithosBlock);

	/**
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param source_file
	 *            : the absolute path of the file that should be uploaded/stored
	 *            to pithos storage system
	 * @return A string that actually is the response code and message that
	 *         identifies the result of the current process based on the
	 *         corresponding response codes as they are described into
	 *         {@link https
	 *         ://www.synnefo.org/docs/synnefo/latest/object-api-guide.html}
	 */
	public String uploadFileToPithos(String pithos_container, String source_file);

	/**
	 * Stream primitive data as bytes to Pithos storage system. It should be
	 * identified the type of the data that is going to be uploaded to Pithos,
	 * so as the outputstream to be configured appropriately.
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param object_location
	 *            : the path (including the name of the new file) that will be
	 *            created on pithos
	 * @return A string that actually is the response code and message that
	 *         identifies the result of the current process based on the
	 *         corresponding response codes as they are described into
	 *         {@link https

	 */
	public String createEmptyPithosObject(String pithos_container,
			PithosObject pithos_object);

	/**
	 * Performs the move of a selected pithos object that is in the root of the
	 * selected container, to a specific target folder into the same (selected)
	 * container
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            corresponds to 'Pithos'
	 * @param target_object
	 *            : the object that should be moved
	 * @param target_folder_path
	 *            : the full path of the folder that the object will be moved
	 * @return A string that actually is the response code and message that
	 *         identifies the result of the current process based on the
	 *         corresponding response codes as they are described into
	 *         {@link https

	 */
	public String movePithosObjectToFolder(String pithos_container,
			String target_object, String target_folder_path);

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
	 * @return A string that actually is the response code and message that
	 *         identifies the result of the current process based on the
	 *         corresponding response codes as they are described into
	 *         {@link https
	 *         ://www.synnefo.org/docs/synnefo/latest/object-api-guide.html}
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
	 * @param target_object
	 *            : the object on which will stream block data on
	 * @param pithos_block
	 *            : the actuall block instance that should be created before and
	 *            sent after to system store
	 * 
	 * @return A string that actually is the response code and message that
	 *         identifies the result of the current process based on the
	 *         corresponding response codes as they are described into
	 *         {@link https
	 *         ://www.synnefo.org/docs/synnefo/latest/object-api-guide.html}
	 */
	public String pithosBlockOutputStream(String pithos_container,
			String target_object, PithosBlock pithos_block);

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
	public boolean pithosObjectBlockExists(String pithos_container,
			String blockHash);

	/**
	 * Return an array of pithos blocks as a Java File object
	 * 
	 * @param pithosBlockArray
	 *            the PithosBlock array with the pithos blocks that constitute a
	 *            Hadoop block.
	 * 
	 * @param offsetIntoBlock
	 *            the long offSet used to read from a pithos block.
	 * 
	 * @return return a Java File object that is made up from the pithos blocks
	 *         in pithosBlockArray
	 */
	public File retrieveBlock(String pithos_container,
			String target_object, long target, long targetBlockEnd);

}
