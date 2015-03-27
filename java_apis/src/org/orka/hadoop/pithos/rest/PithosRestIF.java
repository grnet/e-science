package org.orka.hadoop.pithos.rest;

import java.io.File;
import java.io.InputStream;
import java.util.Collection;

import org.apache.hadoop.fs.FSDataInputStream;

import gr.grnet.escience.fs.pithos.PithosObjectBlock;

public interface PithosRestIF {

	/**************************
	 * PITHOS CONTAINER LEVEL
	 **************************/
	public PithosResponse getContainerInfo(String pithos_container);

	/**************************
	 * PITHOS OBJECT LEVEL
	 **************************/
	/**
	 * Copy a file, from the local to the specified Pithos location, as Pithos
	 * Object into the default container
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coresponds to 'Pithos'
	 * @param source_file
	 *            : the location of the file, in the local storage, that will be
	 *            stored into Pithos FS as object
	 * @param pithos_object_location
	 *            : the location into Pithos default container, where the local
	 *            file will be stored as object
	 */
	public void createPithosObject(String pithos_container,
			String source_file, String pithos_object_location);

	/**
	 * Uploads a file, from the local to the specified Pithos location, as
	 * Pithos Object into the default container. The difference with the
	 * 'createObjectToPithos' methods, refers to the fact that the current
	 * method creates a direct Outputstream from local to Pithos
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coresponds to 'Pithos'
	 * @param source_file
	 *            : the location of the file, in the local storage, that will be
	 *            stored into Pithos FS as object
	 * @param pithos_object_location
	 *            : the location into Pithos default container, where the local
	 *            file will be stored as object
	 */
	public void uploadPithosObject(String pithos_container,
			String source_file, String destination_file);

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
	public File getPithosObject(String pithos_container,
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
	public long getPithosObjectSize(String pithos_container, String object_location);

	/**
	 * Downloads and stores on the defined destination location, a chunk of the
	 * defined object from Pithos, without the definition of particular chunk
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coressponds to 'Pithos'
	 * @param object_location
	 *            : the location of the object into the Pithos default container
	 * @param destination_file
	 *            : the location where the requested Pithos object chunk will be
	 *            downloaded and stored
	 * @param object_size_in_bytes
	 *            : the size in bytes of the object chunk that will be
	 *            downloaded and stored on the destination
	 */
	public PithosObjectBlock getPithosObjectBlock(String pithos_container,
			String object_location, String block_hash);

	/**
	 * Get the hashes of all blocks that comprise the requested object
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coressponds to 'Pithos'
	 * @param object_location
	 *            : the location of the object into the Pithos default container
	 * @return a collection of Strings that each String corresponds to hash code
	 *         of the available blocks
	 */
	public Collection<String> getPithosObjectBlockHashes(String pithos_container,
			String object_location);

	/**
	 * Downloads and stores on the defined destination location, a chunk of the
	 * defined object from Pithos, without the definition of particular chunk
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coresponds to 'Pithos'
	 * @param object_location
	 *            : the location of the object into the Pithos default container
	 * @param destination_file
	 *            : the location where the requested Pithos object chunk will be
	 *            downloaded and stored
	 * @param blocks_number
	 *            : the number of the blocks that should be downloaded and
	 *            stored on the destination
	 */
	public PithosObjectBlock[] getPithosObjectBlockAll(
			String pithos_container, String object_location);

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
	public long getPithosObjectBlockDefaultSize(String pithos_container);

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
	 * the Hadoop ecosystem is running
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coresponds to 'Pithos'
	 * @param object_location
	 *            : the location of the object, that it is requested to be read,
	 *            in Pithos
	 */
	public FSDataInputStream readPithosObject(String pithos_container,
			String object_location);

	/**
	 * Read the data of an object chunk that is available in Pithos, by using an
	 * InputStream, without the need to store the data on the local system where
	 * the Hadoop ecosystem is running
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
	public InputStream readPithosObjectBlock(String pithos_container,
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
	 * Create a new directory / folder on the Pithos storage system, into the
	 * default container
	 * 
	 * @param pithos_container
	 *            : the Pithos container on which the action will be performed.
	 *            Leave it blank so as to refer to the default container that
	 *            coresponds to 'Pithos'
	 * @param object_name
	 *            : the name of the directory that will be created into the
	 *            default container
	 */
	public void mmkdirOnPithos(String pithos_container, String directory_name);

}
