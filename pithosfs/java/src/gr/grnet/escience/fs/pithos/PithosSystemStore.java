package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.pithos.rest.PithosResponse;
import gr.grnet.escience.pithos.rest.PithosResponseFormat;

import java.io.File;
import java.io.IOException;
import java.util.Collection;

import org.apache.hadoop.fs.FSDataInputStream;

public interface PithosSystemStore {

    /**************************
     * PITHOS CONTAINER LEVEL
     **************************/
    /**
     * 
     * @param pithosContainer
     * @return Pithos response in JSON format that includes information about a
     *         selected container on +Pithos as they are identified into the
     *         specifications / API {@link https
     *         ://www.synnefo.org/docs/synnefo/latest/object-api-guide.html}
     * @throws IOException
     *             TODO
     */

    public PithosResponse getContainerInfo(String pithosContainer)
            throws IOException;

    /**
     * 
     * @param pithosContainer
     * @return The list of available files into the selected container.
     * @throws IOException
     *             TODO
     */
    public String getFileList(String pithosContainer) throws IOException;

    /**************************
     * PITHOS OBJECT LEVEL
     **************************/
    /***
     * Downloads and stores on the defined destination location, the overall
     * object from pithos, without the definition of particular chunk
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            coresponds to 'Pithos'
     * @param objectLocation
     *            : the location of the object into the Pithos default container
     * @param object_destination_location
     *            : the location where the requested Pithos object will be
     *            downloaded and stored
     */
    public File retrievePithosObject(String pithosContainer,
            String objectLocation, String destinationFile);

    /**
     * Get the total size of a Pithos object that is available into the selected
     * container
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            coresponds to 'Pithos'
     * @param objectLocation
     *            : the location of the object into the Pithos default container
     * @return the total size in bytes of the requested Pithos Object
     */
    public long getPithosObjectSize(String pithosContainer,
            String objectLocation);

    /**
     * Downloads and stores on the defined destination location, a chunk of the
     * defined object from Pithos, without the definition of particular chunk
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param targetObject
     *            : the object of which the block will be retrieved
     * @param blockHash
     *            : the hash code of the block that will be retrieved
     */
    public PithosBlock retrievePithosBlock(String pithosContainer,
            String targetObject, String blockHash);

    /**
     * Get the hashes of all blocks that comprise the requested object
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param objectLocation
     *            : the location of the object into the Pithos default container
     * @return a collection of Strings that each String corresponds to hash code
     *         of the available blocks
     */
    public Collection<String> getPithosObjectBlockHashes(
            String pithosContainer, String objectLocation);

    /**
     * Downloads and stores on the defined destination location, a chunk of the
     * defined object from Pithos, without the definition of particular chunk
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            coresponds to 'Pithos'
     * @param targetObject
     *            : the location of the object into the Pithos default container
     *            that should be retrieved
     */
    public PithosBlock[] retrievePithosObjectBlocks(String pithosContainer,
            String targetObject);

    /**
     * Get the total number of the blocks that comprise the overal block
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            coresponds to 'Pithos'
     * @param objectLocation
     *            : the location of the object into the Pithos default container
     * @return: the total number of the blocks that comprise the Object
     */
    public int getPithosObjectBlocksNumber(String pithosContainer,
            String objectLocation);

    /**
     * Get the current size of the requested object in bytes
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param objectLocation
     *            : the object that its block size will be checked
     */
    public long getPithosObjectBlockSize(String pithosContainer,
            String objectLocation);

    /**
     * Get the default object size in bytes that is defined for the specified
     * container. The default block size is included in the Container info.
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @throws IOException
     *             TODO
     */
    public long getPithosBlockDefaultSize(String pithosContainer)
            throws IOException;

    /**
     * Get the hash algorithm used to compute the digest of blocks stored in
     * container
     * 
     * 
     * @param pithosContainer
     *            : the Pithos container queried
     * @return : name of hash algorithm used
     * @throws IOException
     *             TODO
     */
    public String getPithosContainerHashAlgorithm(String pithosContainer)
            throws IOException;

    /***
     * Method to get the meta-data that correspond to a Pithos object stored
     * under the default ("Pithos")
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            coresponds to 'Pithos'
     * @param objectLocation
     *            : the location of the requested object into Pithos storage
     *            system
     * @param format
     *            : the format in which the object meta-data will be received
     * @return a string that corresponds to the set of meta-data for the
     *         requested object in the specified format (JSON or XML)
     */
    public PithosResponse getPithosObjectMetaData(String pithosContainer,
            String objectLocation, PithosResponseFormat format);

    /**
     * Read the data of the object that is available in Pithos, by using an
     * InputStream, without the need to store the data on the local system where
     * the Hadoop ecosystem is running. Essentially it feeds directly Hadoop
     * with data from the object
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            coresponds to 'Pithos'
     * @param objectLocation
     *            : the location of the object, that it is requested to be read,
     *            in Pithos
     */
    public FSDataInputStream pithosObjectInputStream(String pithosContainer,
            String objectLocation);

    /**
     * Read the data of an object chunk that is available in Pithos, by using an
     * InputStream, without the need to store the data on the local system where
     * the Hadoop ecosystem is running. Essentially it feeds directly Hadoop
     * with data from the object
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param objectLocation
     *            : the location of the object, that it is requested to be read,
     *            in Pithos
     * @param blockHash
     *            : the hash code of the requested block
     * @return The input stream of the block data as FSDataInputStream
     */
    public FSDataInputStream pithosBlockInputStream(String pithosContainer,
            String objectLocation, String blockHash);

    /**
     * Read the data of an object chunk that is available in Pithos, by using an
     * InputStream, without the need to store the data on the local system where
     * the Hadoop ecosystem is running. Essentially it feeds directly Hadoop
     * with data from the object
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param objectLocation
     *            : the location of the object, that it is requested to be read,
     *            in Pithos
     * @param blockHash
     *            : the hash code of the requested block
     * @param offsetIntoPithosBlock
     *            : the starting point of the range for the retrieved data
     * @return The input stream of the block data as FSDataInputStream
     */
    public File pithosBlockInputStream(String pithosContainer,
            String objectLocation, String blockHash, long offsetIntoPithosBlock);

    /**
     * Delete the defined object from Pithos container
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param objectLocation
     *            : the location of the object in Pithos
     */
    public void deletePithosObject(String pithosContainer, String objectLocation);

    /**
     * Delete a block on Pithos storage system, by using its unique hash code
     * 
     * @param blockHash
     *            : the block hash that is going to be deleted
     */
    public void deletePithosBlock(String blockHash);

    /**
     * Uploads a file, from the local to the specified Pithos location, as
     * Pithos Object into the default container. The difference with the
     * 'createObjectToPithos' methods, refers to the fact that the current
     * method creates a direct Outputstream from local to Pithos
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param objectName
     *            : the name of the object that will be created on Pithos system
     *            Store
     * @param pithosObject
     *            : the Pithos Object structured class object that packs the
     *            data into Pithos object structure and it will be stored on
     *            Pithos storage systme
     * @throws IOException
     *             TODO
     */
    public String storePithosObject(String pithosContainer,
            PithosObject pithosObject) throws IOException;

    /**
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param targetObject
     *            : the name of the object on which the block will be appended
     * @param pithosBlock
     *            : the actual Pithos Block that will be stored on Pithos
     *            storage system
     * @param backupFile
     *            : the temporary file storing the block data to be streamed
     * @return A string that actually is the response code and message that
     *         identifies the result of the current process based on the
     *         corresponding response codes as they are described into
     *         {@link https
     *         ://www.synnefo.org/docs/synnefo/latest/object-api-guide.html}
     */
    public String storePithosBlock(String pithosContainer, String targetObject,
            PithosBlock pithosBlock, File backupFile);

    /**
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param targetObject
     *            : the name of the object on which the block will be appended
     * @param newPithosBlock
     *            : the actual Pithos Block that will be appended to the target
     *            object
     * @return A string that actually is the response code and message that
     *         identifies the result of the current process based on the
     *         corresponding response codes as they are described into
     *         {@link https
     *         ://www.synnefo.org/docs/synnefo/latest/object-api-guide.html}
     * @throws IOException
     *             TODO
     */
    public String appendPithosBlock(String pithosContainer,
            String targetObject, PithosBlock newPithosBlock) throws IOException;

    /**
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param sourceFile
     *            : the absolute path of the file that should be uploaded/stored
     *            to pithos storage system
     * @return A string that actually is the response code and message that
     *         identifies the result of the current process based on the
     *         corresponding response codes as they are described into
     *         {@link https
     *         ://www.synnefo.org/docs/synnefo/latest/object-api-guide.html}
     * @throws IOException
     *             TODO
     */
    public String uploadFileToPithos(String pithosContainer, String sourceFile)
            throws IOException;

    /**
     * @throws IOException
     *             TODO Stream primitive data as bytes to Pithos storage system.
     *             It should be identified the type of the data that is going to
     *             be uploaded to Pithos, so as the outputstream to be
     *             configured appropriately.
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param objectLocation
     *            : the path (including the name of the new file) that will be
     *            created on pithos
     * @return A string that actually is the response code and message that
     *         identifies the result of the current process based on the
     *         corresponding response codes as they are described into
     *         {@link https

     */
    public String createEmptyPithosObject(String pithosContainer,
            PithosObject pithosObject) throws IOException;

    /**
     * @throws IOException
     *             TODO Performs the move of a selected pithos object that is in
     *             the root of the selected container, to a specific target
     *             folder into the same (selected) container
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param targetObject
     *            : the object that should be moved
     * @param targetFolderPath
     *            : the full path of the folder that the object will be moved
     * @return A string that actually is the response code and message that
     *         identifies the result of the current process based on the
     *         corresponding response codes as they are described into
     *         {@link https

     */
    public String movePithosObjectToFolder(String pithosContainer,
            String targetObject, String targetFolderPath) throws IOException;

    /**
     * This method gets as input the container of the Pithos storage system, the
     * name of a Pithos Object instance and the actual object instance and send
     * the data to Pithos by streaming them to Pithos
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param pithosObject
     *            : a Pithos Object instance that stores the data of the object
     *            that will be stored on Pithos storage system
     * 
     * @return A string that actually is the response code and message that
     *         identifies the result of the current process based on the
     *         corresponding response codes as they are described into
     *         {@link https
     *         ://www.synnefo.org/docs/synnefo/latest/object-api-guide.html}
     */
    public String pithosObjectOutputStream(String pithosContainer,
            String objectName, PithosObject pithosObject);

    /**
     * This method gets as input the container of the Pithos storage system, the
     * hash code of an Object Block instance and the actual block instance and
     * append the object to Pithos through an output streaming
     * 
     * @param pithosContainer
     *            : the Pithos container on which the action will be performed.
     *            Leave it blank so as to refer to the default container that
     *            corresponds to 'Pithos'
     * @param targetObject
     *            : the object on which will stream block data on
     * @param pithosBlock
     *            : the actuall block instance that should be created before and
     *            sent after to system store
     * 
     * @return A string that actually is the response code and message that
     *         identifies the result of the current process based on the
     *         corresponding response codes as they are described into
     *         {@link https
     *         ://www.synnefo.org/docs/synnefo/latest/object-api-guide.html}
     */
    public String pithosBlockOutputStream(String pithosContainer,
            String targetObject, PithosBlock pithosBlock);

    /**
     * 
     * @param pithosContainer
     * @param pithosObjectName
     * @return <b>true</b> if the object exists and <b>false</b> if not
     * @throws IOException
     *             TODO
     */
    public boolean pithosObjectExists(String pithosContainer,
            String pithosObjectName) throws IOException;

    /**
     * This method search for existing blocks on Pithos storage system by using
     * a given hash code by the user
     * 
     * @param blockHash
     *            : the hash code of the requested block
     * @return <b>true</b> if the block exists and <b>false</b> if not
     */
    public boolean pithosObjectBlockExists(String pithosContainer,
            String blockHash);

    /**
     * Return a stream of pithos blocks as a Java File object
     * 
     * @param pithosContainer
     *            the Pithos container where the requested pithos file belongs.
     * 
     * @param targetObject
     *            the Pithos file to be read.
     * 
     * @param targetBlockStart
     *            the start of the byte range to be read.
     * 
     * @param targetBlockEnd
     *            the end of the byte range to be read.
     * 
     * @return return a Java File object that is made up from pithos blocks
     */
    public File retrievePithosBlocks(String pithosContainer,
            String targetObject, long targetBlockStart, long targetBlockEnd);

}
