package gr.grnet.escience.pithos.rest;

import gr.grnet.escience.commons.PithosSerializer;
import gr.grnet.escience.commons.Utils;
import gr.grnet.escience.fs.pithos.PithosBlock;
import gr.grnet.escience.fs.pithos.PithosInputStream;
import gr.grnet.escience.fs.pithos.PithosObject;
import gr.grnet.escience.fs.pithos.PithosPath;
import gr.grnet.escience.fs.pithos.PithosSystemStore;
import gr.grnet.escience.pithos.restapi.PithosRESTAPI;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.util.Base64;
import java.util.Collection;
import java.util.List;
import java.util.Map;

import org.apache.hadoop.fs.FSDataInputStream;

import com.google.gson.Gson;

/***
 * This class builds on top of Pithos REST API Java implementation by grnet
 * adding methods more specific to interaction between Hadoop and Pithos Storage
 * System.
 * 
 * @see <a href="https://www.synnefo.org/docs/synnefo/latest/object-api-guide.html#object-level">object-api-guide.html#object-level</a>
 * 
 * @author dkelaidonis
 * @version 0.1
 * @since March, 2015
 */

public class HadoopPithosConnector extends PithosRESTAPI implements
        PithosSystemStore {

    private static final long serialVersionUID = 1L;

    private transient PithosRequest request;

    private transient PithosResponse response;

    /** holds a reference to the source file or folder to upload to pithos fs. */
    private transient Object srcFile2bUploaded;

    private File temp;

    private File blockData;

    private transient InputStream pithosFileInputStream;

    /** Object data as a base64 encoded string */
    private String objectDataContent;

    private String responseStr;

    private transient PithosPath path;

    private long[] range = { 0, 0 };

    private long currentSize = 0;

    private transient Map<String, List<String>> responseData = null;

    /** The hash map response. */
    private transient PithosResponseHashmap hashMapResp = null;

    private long objectTotalSize = 0;

    private long blockSize = 0;

    private int objectBlocksNumber = 0;

    private long[] blockBytesRange = null;

    private transient Collection<String> objectBlockHashes = null;

    int blockLocationPointerCounter = 1;

    int blockLocationPointer = 0;

    private transient PithosBlock resultPithosBlock = null;

    private transient PithosBlock[] blocks = null;

    private transient PithosResponse genericResponse = null;

    private String hashAlgo = null;

    /** holds an encoded string. */
    private String encString = null;

    private transient FSDataInputStream fsDataInputStream = null;

    private transient PithosInputStream pithosInputStream = null;

    private File pithosBlockData = null;

    private File tmpFile2bUploaded = null;

    private String contentLength = null;

    /**
     * *** Constructor.
     *
     * @param pithosUrl
     *            the pithos url
     * @param pithosToken
     *            the pithos token
     * @param uuid
     *            the uuid
     */
    public HadoopPithosConnector(String pithosUrl, String pithosToken,
            String uuid) {
        // - Implement aPithos RESTAPI instance
        super(pithosUrl, pithosToken, uuid);
    }

    /**
     * Terminate connection.
     */
    public void terminateConnection() {
        Utils.dbgPrint("ERROR: Unauthorized. Authentication Token is not valid.");
    }

    private PithosRequest getPithosRequest() {
        return request;
    }

    private void setPithosRequest(PithosRequest request) {
        this.request = request;
    }

    private PithosResponse getPithosResponse() {
        return response;
    }

    private void setPithosResponse(PithosResponse response) {
        this.response = response;
    }

    /**
     * Manage Blocks.
     *
     * @param objectTotalSize
     *            the object total size
     * @param blockSize
     *            the block size
     * @param blocksNumber
     *            the blocks number
     * @param blockPointer
     *            the block pointer
     * @return the long[]
     */
    private long[] bytesRange(long objectTotalSize, long blockSize,
            int blocksNumber, int blockPointer) {
        // - Initialize a long array that will keep 2 values; one for the start
        // of the range and one for the end of the range of bytes
        range = null;
        range = new long[2];
        // - Create
        currentSize = 0;

        // - Check if there are more than one blocks
        if (blocksNumber > 1) {
            // - if the requested block is the first one
            if (blockPointer == 1) {
                // - Get range start
                range[0] = currentSize;
                // - Get range stop
                range[1] = blockSize - 1;
            }
            // - if the requested block is the last one
            else if (blockPointer == blocksNumber) {
                int previousBlocks = blocksNumber - 1;
                long previousSize = blockSize * previousBlocks;
                long lastBlockSize = objectTotalSize - previousSize;
                // - Get range start
                range[0] = (objectTotalSize - lastBlockSize);

                // - Get range stop
                range[1] = objectTotalSize - 1;

            } else {
                // - Any intermediate block
                for (int i = 1; i <= blocksNumber; i++) {
                    // - if the current block is the requested one
                    if (i == blockPointer) {
                        // - Get range start
                        range[0] = currentSize;

                        // - Get range stop
                        range[1] = range[0] + blockSize - 1;

                        // - stop the loop
                        break;
                    }

                    currentSize = (currentSize + blockSize);
                }
            }
        } else {
            // - Get range start
            range[0] = 0;
            // - Get range stop
            range[1] = objectTotalSize - 1;
        }

        // - Return the table
        return range;
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#getContainerInfo(java.lang
     * .String)
     */
    @Override
    public PithosResponse getContainerInfo(String pithosContainer) {
        // - Create Pithos request
        setPithosRequest(new PithosRequest());

        // - Create Response instance
        setPithosResponse(new PithosResponse());

        // - Read meta-data and add the data on the Pithos Response
        try {
            // - If container argument is empty the initialize it with the
            // default value
            if ("".equals(pithosContainer)) {
                pithosContainer = "pithos";
            }

            // - Add data from pithos response on the corresponding java object
            getPithosResponse().setResponseData(
                    retrieve_container_info(pithosContainer, getPithosRequest()
                            .getRequestParameters(), getPithosRequest()
                            .getRequestHeaders()));

        } catch (IOException e) {
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        }

        // - Return the response data as String
        return getPithosResponse();
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#getFileList(java.lang.String
     * )
     */
    @Override
    public String getFileList(String pithosContainer) {
        // - Create Pithos request
        setPithosRequest(new PithosRequest());

        // - Create Response instance
        setPithosResponse(new PithosResponse());
        responseData = null;
        // - Read meta-data and add the data on the Pithos Response
        try {
            // - Perform action by using Pithos REST API method
            // - Return the response data as String
            return list_container_objects(pithosContainer, getPithosRequest()
                    .getRequestParameters(), getPithosRequest()
                    .getRequestHeaders());
        } catch (IOException e) {
            // - Return the exception message as String
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#retrievePithosObject(java
     * .lang.String, java.lang.String, java.lang.String)
     */
    @Override
    public File retrievePithosObject(String pithosContainer,
            String objectLocation, String destinationFile) {
        // - Create Pithos request
        setPithosRequest(new PithosRequest());

        // - Request Parameters
        // - JSON Format
        getPithosRequest().getRequestParameters().put("format", "json");

        // - Read data object
        try {

            return (File) read_object_data(objectLocation, pithosContainer,
                    getPithosRequest().getRequestParameters(),
                    getPithosRequest().getRequestHeaders());
        } catch (IOException e) {
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#getPithosObjectSize(java
     * .lang.String, java.lang.String)
     */
    @Override
    public long getPithosObjectSize(String pithosContainer,
            String objectLocation) {
        // - Create Pithos request
        setPithosRequest(new PithosRequest());

        // - Request Parameters
        // - JSON Format
        getPithosRequest().getRequestParameters().put("format", "json");
        getPithosRequest().getRequestParameters().put("hashmap", "True");

        hashMapResp = null;

        // - Read data object
        try {
            // -Serialize json response into Java object PithosResponseHashmap
            hashMapResp = (new Gson()).fromJson(
                    (String) read_object_data(objectLocation, pithosContainer,
                            getPithosRequest().getRequestParameters(),
                            getPithosRequest().getRequestHeaders()),
                    PithosResponseHashmap.class);

            // - Return the required value
            if (hashMapResp != null) {
                return Long.parseLong(hashMapResp.getObjectSize());
            } else {
                return -1;
            }
        } catch (IOException e) {
            hashMapResp = null;
            Utils.dbgPrint(e.getMessage(), e);
            return -1;
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#retrievePithosBlock(java
     * .lang.String, java.lang.String, java.lang.String)
     */
    @Override
    public PithosBlock retrievePithosBlock(String pithosContainer,
            String objectLocation, String blockHash) {

        // - Get required info for the object and the block
        objectTotalSize = getPithosObjectSize(pithosContainer, objectLocation);
        blockSize = getPithosObjectBlockSize(pithosContainer, objectLocation);
        objectBlocksNumber = getPithosObjectBlocksNumber(pithosContainer,
                objectLocation);

        objectBlockHashes = getPithosObjectBlockHashes(pithosContainer,
                objectLocation);

        // - Iterate on available hashes
        blockLocationPointerCounter = 1;
        blockLocationPointer = 0;

        for (String hash : objectBlockHashes) {
            // - If the hash is the requested hash
            if (hash.equals(blockHash)) {
                // - Get the location of the block
                blockLocationPointer = blockLocationPointerCounter;
                break;
            }
            // - Move the pointer one step forward
            blockLocationPointerCounter++;
        }

        // - Get the Range of the byte for the requested block
        blockBytesRange = null;
        blockBytesRange = bytesRange(objectTotalSize, blockSize,
                objectBlocksNumber, blockLocationPointer);

        // - Create byte array for the object
        // - Create Pithos request
        setPithosRequest(new PithosRequest());

        // - Request Parameters
        // - JSON Format
        getPithosRequest().getRequestParameters().put("format", "json");
        // - Add requested parameter for the range
        // - If it is not requested the last block, the add specific range
        if (blockBytesRange[1] != objectTotalSize - 1) {
            getPithosRequest().getRequestHeaders().put("Range",
                    "bytes=" + blockBytesRange[0] + "-" + blockBytesRange[1]);
        } else {
            getPithosRequest().getRequestHeaders().put("Range",
                    "bytes=" + blockBytesRange[0] + "-");
        }

        // - Read data object
        try {
            // - Get the chunk of the pithos object as a file
            blockData = (File) read_object_data(objectLocation,
                    pithosContainer, getPithosRequest().getRequestParameters(),
                    getPithosRequest().getRequestHeaders());

            resultPithosBlock = new PithosBlock(blockHash, blockData.length(),
                    PithosSerializer.serializeFile(blockData));

            // - Return the created pithos object
            return resultPithosBlock;
        } catch (IOException e) {
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        } finally {
            if (blockData != null) {
                blockData = null;
            }
            if (resultPithosBlock != null) {
                resultPithosBlock = null;
            }
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#getPithosObjectBlocksNumber
     * (java.lang.String, java.lang.String)
     */
    @Override
    public int getPithosObjectBlocksNumber(String pithosContainer,
            String objectLocation) {

        // - Create Pithos request
        setPithosRequest(new PithosRequest());

        // - Request Parameters
        // - JSON Format
        getPithosRequest().getRequestParameters().put("format", "json");
        getPithosRequest().getRequestParameters().put("hashmap", "True");

        // - Read data object
        try {
            // -Serialize json response into Java object PithosResponseHashmap
            hashMapResp = (new Gson()).fromJson(
                    (String) read_object_data(objectLocation, pithosContainer,
                            getPithosRequest().getRequestParameters(),
                            getPithosRequest().getRequestHeaders()),
                    PithosResponseHashmap.class);
            // - Return the required value
            return hashMapResp.getBlockHashes().size();
        } catch (IOException e) {
            Utils.dbgPrint(e.getMessage(), e);
            return -1;
        } finally {
            if (hashMapResp != null) {
                hashMapResp = null;
            }
        }

    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#getPithosObjectBlockHashes
     * (java.lang.String, java.lang.String)
     */
    @Override
    public Collection<String> getPithosObjectBlockHashes(
            String pithosContainer, String objectLocation) {
        // - Create Pithos request
        setPithosRequest(new PithosRequest());

        // - Request Parameters
        // - JSON Format
        getPithosRequest().getRequestParameters().put("format", "json");
        getPithosRequest().getRequestParameters().put("hashmap", "True");

        // - Read data object
        try {
            // -Serialize json response into Java object PithosResponseHashmap
            hashMapResp = (new Gson()).fromJson(
                    (String) read_object_data(objectLocation, pithosContainer,
                            getPithosRequest().getRequestParameters(),
                            getPithosRequest().getRequestHeaders()),
                    PithosResponseHashmap.class);
            // - Return the required value
            return hashMapResp.getBlockHashes();
        } catch (IOException e) {
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        } finally {
            if (hashMapResp != null) {
                hashMapResp = null;
            }
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#retrievePithosObjectBlocks
     * (java.lang.String, java.lang.String)
     */
    @Override
    public PithosBlock[] retrievePithosObjectBlocks(String pithosContainer,
            String objectLocation) {
        // - Create local blocks Array
        blocks = null;

        // - Get the hashes of the blocks for the requested object
        Collection<String> blockHashes = getPithosObjectBlockHashes(
                pithosContainer, objectLocation);

        // - Initialize the local blocks array
        blocks = new PithosBlock[blockHashes.size()];

        // - Get and store on array all the available blocks
        int blockCounter = 0;
        for (String hash : blockHashes) {
            blocks[blockCounter] = retrievePithosBlock(pithosContainer,
                    objectLocation, hash);

            // - Next block
            blockCounter++;
        }

        return blocks;
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#getPithosObjectBlockSize
     * (java.lang.String, java.lang.String)
     */
    @Override
    public long getPithosObjectBlockSize(String pithosContainer,
            String objectLocation) {

        // - Create Pithos request
        setPithosRequest(new PithosRequest());

        // - Request Parameters
        // - JSON Format
        getPithosRequest().getRequestParameters().put("format", "json");
        getPithosRequest().getRequestParameters().put("hashmap", "True");

        // - Read data object
        try {
            // -Serialize json response into Java object PithosResponseHashmap
            hashMapResp = (new Gson()).fromJson(
                    (String) read_object_data(objectLocation, pithosContainer,
                            getPithosRequest().getRequestParameters(),
                            getPithosRequest().getRequestHeaders()),
                    PithosResponseHashmap.class);
            // - Return the required value
            return Long.parseLong(hashMapResp.getBlockSize());
        } catch (IOException e) {
            Utils.dbgPrint(e.getMessage(), e);
            return -1;
        } finally {
            if (hashMapResp != null) {
                hashMapResp = null;
            }
        }

    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#getPithosBlockDefaultSize
     * (java.lang.String)
     */
    @Override
    public long getPithosBlockDefaultSize(String pithosContainer) {
        // - Create response object
        genericResponse = (new Gson()).fromJson(
                (new Gson()).toJson(getContainerInfo(pithosContainer)),
                PithosResponse.class);

        // - Return the value of the block size
        return Long.parseLong(genericResponse.getResponseData()
                .get("X-Container-Block-Size").get(0));

    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#getPithosContainerHashAlgorithm
     * (java.lang.String)
     */
    @Override
    public String getPithosContainerHashAlgorithm(String pithosContainer) {
        // - Create response object
        genericResponse = (new Gson()).fromJson(
                (new Gson()).toJson(getContainerInfo(pithosContainer)),
                PithosResponse.class);
        // - Return the name of the hash algorithm
        hashAlgo = genericResponse.getResponseData()
                .get("X-Container-Block-Hash").get(0);
        return Utils.fixPithosHashName(hashAlgo);
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#getPithosObjectMetaData
     * (java.lang.String, java.lang.String,
     * gr.grnet.escience.pithos.rest.PithosResponseFormat)
     */
    @Override
    public PithosResponse getPithosObjectMetaData(String pithosContainer,
            String objectLocation, PithosResponseFormat format) {
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
            responseData = null;
            responseData = retrieve_object_metadata(objectLocation,
                    pithosContainer, getPithosRequest().getRequestParameters(),
                    getPithosRequest().getRequestHeaders());

            // - Add data from pithos response on the corresponding java object
            getPithosResponse().setResponseData(responseData);

        } catch (IOException e) {
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        }

        // - Return Pithos Response object as the result
        return getPithosResponse();
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#pithosObjectInputStream
     * (java.lang.String, java.lang.String)
     */
    @Override
    public FSDataInputStream pithosObjectInputStream(String pithosContainer,
            String objectLocation) {

        // - Release potential unused data
        fsDataInputStream = null;
        pithosInputStream = null;

        // - Create input stream for pithos
        try {

            pithosInputStream = new PithosInputStream(pithosContainer,
                    objectLocation);

            fsDataInputStream = new FSDataInputStream(pithosInputStream);

            // - Return the input stream wrapped into a FSDataINputStream
            return fsDataInputStream;
        } catch (Exception e) {
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        } finally {
            // - Release potential unused data
            fsDataInputStream = null;
            pithosInputStream = null;
        }

    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#pithosBlockInputStream(
     * java.lang.String, java.lang.String, java.lang.String)
     */
    @Override
    public FSDataInputStream pithosBlockInputStream(String pithosContainer,
            String objectLocation, String blockHash) {
        // - Create input stream for Pithos
        try {
            if (pithosFileInputStream != null) {
                pithosFileInputStream.close();
                pithosFileInputStream = null;
            }

            // - Get the file object from pithos
            resultPithosBlock = retrievePithosBlock(pithosContainer,
                    objectLocation, blockHash);

            // - Add File data to the input stream
            pithosBlockData = PithosSerializer
                    .deserializeFile(resultPithosBlock.getBlockData());

            // - Create File input stream
            pithosFileInputStream = new FileInputStream(pithosBlockData);

            // - Return the input stream wrapped into a FSDataINputStream
            // return pithosFileInputStream;
            fsDataInputStream = new FSDataInputStream(pithosFileInputStream);
            return fsDataInputStream;
        } catch (IOException e) {
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        } finally {
            resultPithosBlock = null;
            pithosBlockData = null;
            fsDataInputStream = null;
        }

    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#pithosBlockInputStream(
     * java.lang.String, java.lang.String, java.lang.String, long)
     */
    @Override
    public File pithosBlockInputStream(String pithosContainer,
            String objectLocation, String blockHash, long offsetIntoPithosBlock) {

        // - Get required info for the object and the block
        objectTotalSize = getPithosObjectSize(pithosContainer, objectLocation);
        blockSize = getPithosObjectBlockSize(pithosContainer, objectLocation);
        objectBlocksNumber = getPithosObjectBlocksNumber(pithosContainer,
                objectLocation);

        objectBlockHashes = getPithosObjectBlockHashes(pithosContainer,
                objectLocation);

        // - Iterate on available hashes
        blockLocationPointerCounter = 1;
        for (String hash : objectBlockHashes) {
            // - If the hash is the requested hash
            if (hash.equals(blockHash)) {
                break;
            }
            // - Move the pointer one step forward
            blockLocationPointerCounter++;
        }

        // - Find the bytes range of the current block
        range = bytesRange(objectTotalSize, blockSize, objectBlocksNumber,
                blockLocationPointerCounter);

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
                blockData = (File) read_object_data(objectLocation,
                        pithosContainer, getPithosRequest()
                                .getRequestParameters(), getPithosRequest()
                                .getRequestHeaders());

                // -Return the actual data of after the block seek
                return blockData;
            } catch (IOException e) {
                Utils.dbgPrint(e.getMessage(), e);
                return null;
            } finally {
                if (blockData != null) {
                    blockData.delete();
                    blockData = null;
                }
            }
        } else {
            return null;
        }

    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#deletePithosObject(java
     * .lang.String, java.lang.String)
     */
    @Override
    public String deletePithosObject(String pithosContainer,
            String objectLocation) {
        // - Create Pithos request
        setPithosRequest(new PithosRequest());

        String strResp = "";
        try {
            strResp = delete_object(objectLocation, pithosContainer,
                    getPithosRequest().getRequestParameters(),
                    getPithosRequest().getRequestHeaders());
        } catch (IOException e) {
            Utils.dbgPrint(e.getMessage(), e);
        }
        return strResp;
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#deletePithosBlock(java.
     * lang.String)
     */
    @Override
    public void deletePithosBlock(String blockHash) {
        // NYI

    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#pithosObjectExists(java
     * .lang.String, java.lang.String)
     */
    @Override
    public boolean pithosObjectExists(String pithosContainer,
            String pithosObjectName) {

        return getFileList(pithosContainer).contains("pithos_object_name");
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#pithosObjectBlockExists
     * (java.lang.String, java.lang.String)
     */
    @Override
    public boolean pithosObjectBlockExists(String pithosContainer,
            String blockHash) {
        // - Get all available object into the container
        return false;
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#storePithosObject(java.
     * lang.String, gr.grnet.escience.fs.pithos.PithosObject)
     */
    @Override
    public String storePithosObject(String pithosContainer,
            PithosObject pithosObject) {
        try {
            // - Create Pithos request
            setPithosRequest(new PithosRequest());

            // - Check if exists and if no, then create it
            if (!getFileList(pithosContainer).contains(pithosObject.getName())) {
                // - Create the file
                createEmptyPithosObject(pithosContainer, pithosObject);

                // - This means that the object should be created
                if (pithosObject.getObjectSize() <= 0) {
                    objectDataContent = "";
                } else {
                    // - Create String from inputstream that corresponds to the
                    // serialized object
                    objectDataContent = PithosSerializer
                            .inputStreamToString(pithosObject.serialize());
                }

                // - Request Parameters
                getPithosRequest().getRequestParameters().put("format", "json");

                // - Request Headers
                getPithosRequest().getRequestHeaders().put("Content-Range",
                        "bytes */*");

                if (pithosObject.getName() != null) {
                    if (!pithosObject.getName().isEmpty()) {
                        return update_append_truncate_object(pithosContainer,
                                pithosObject.getName(), objectDataContent,
                                getPithosRequest().getRequestParameters(),
                                getPithosRequest().getRequestHeaders());
                    } else {
                        return "ERROR: Pithos cannot be empty.";
                    }
                } else {
                    return "ERROR: Pithos object must contain a name.";
                }
            } else {
                return "ERROR: Object <" + pithosObject.getName()
                        + "> already exists.";
            }
        } catch (IOException e) {
            Utils.dbgPrint(e.getMessage(), e);
            return null;

        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#createEmptyPithosObject
     * (java.lang.String, gr.grnet.escience.fs.pithos.PithosObject)
     */
    @Override
    public String createEmptyPithosObject(String pithosContainer,
            PithosObject pithosObject) {
        // - Create Pithos request
        setPithosRequest(new PithosRequest());

        // - Header Parameters
        // - Format of the uploaded file
        getPithosRequest().getRequestHeaders().put("Content-Type",
                "application/octet-stream");

        try {
            // - Create pithos path
            path = new PithosPath(pithosContainer, pithosObject.getName());

            // create a temp file
            temp = File.createTempFile(path.getObjectName(), "");

            // - Get temp file contents into the file that will be uploaded into
            // pithos selected container
            tmpFile2bUploaded = null;
            tmpFile2bUploaded = new File(path.getObjectName());
            temp.renameTo(tmpFile2bUploaded);

            // - Upload file to the root of the selected container
            responseStr = upload_file(tmpFile2bUploaded, null,
                    path.getContainer(), getPithosRequest()
                            .getRequestParameters(), getPithosRequest()
                            .getRequestHeaders());

            // - Check if file should be moved from root pithos to another
            // folder
            if (!path.getObjectFolderAbsolutePath().isEmpty()) {
                // - If the file is successfully upload to the root of pithos
                // container
                if (responseStr.contains("201")) {
                    return movePithosObjectToFolder(path.getContainer(),
                            tmpFile2bUploaded.getName(),
                            path.getObjectFolderAbsolutePath(), null);
                } else {
                    return "ERROR: Fail to create the object into the requested location";
                }
            } else {
                return responseStr;
            }
        } catch (IOException e) {
            // - Return the exception message as String
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        } finally {
            if (temp != null) {
                temp.delete();
            }
            if (srcFile2bUploaded instanceof File && srcFile2bUploaded != null) {
                ((File) srcFile2bUploaded).delete();
            }
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#movePithosObjectToFolder
     * (java.lang.String, java.lang.String, java.lang.String, java.lang.String)
     */
    @Override
    public String movePithosObjectToFolder(String pithosContainer,
            String sourceObject, String targetFolderPath, String targetObject) {
        // - Create Pithos request
        setPithosRequest(new PithosRequest());

        // - Header Parameters
        // - Format of the uploaded file
        getPithosRequest().getRequestParameters().put("format", "json");

        // - Check if the folder path is in appropriate format
        if (!targetFolderPath.isEmpty() && !targetFolderPath.endsWith("/")) {
            targetFolderPath = targetFolderPath.concat("/");
        }
        String toFilename = null;
        if (targetObject == null || targetObject.isEmpty()) {
            toFilename = targetFolderPath.concat(sourceObject);
        } else {
            toFilename = targetFolderPath.concat(targetObject);
        }
        try {
            // - Post data and get the response
            return move_object(pithosContainer, sourceObject, pithosContainer,
                    toFilename, getPithosRequest().getRequestParameters(),
                    getPithosRequest().getRequestHeaders());

        } catch (IOException e) {
            // - Return the exception message as String
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        }

    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#uploadFileToPithos(java
     * .lang.String, java.lang.String, boolean)
     */
    @Override
    public String uploadFileToPithos(String pithosContainer, String sourceFile,
            boolean isDir) {
        // - Create Pithos request
        setPithosRequest(new PithosRequest());

        String strLength = null;
        try {
            if (isDir) {
                srcFile2bUploaded = sourceFile;
                strLength = "0";
                // - Header Parameters
                // - Format of the uploaded file
                getPithosRequest().getRequestHeaders().put("Content-Type",
                        "application/directory");
            }

            else {
                srcFile2bUploaded = new File(sourceFile);
                // - Header Parameters
                // - Format of the uploaded file
                getPithosRequest().getRequestHeaders().put("Content-Type",
                        "application/octet-stream");
            }

            // - If there is successful renaming of the object into the required
            // name
            // - Post data and get the response
            return upload_file(srcFile2bUploaded, strLength, pithosContainer,
                    getPithosRequest().getRequestParameters(),
                    getPithosRequest().getRequestHeaders());
        } catch (IOException e) {
            // - Return the exception message as String
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        }

    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#appendPithosBlock(java.
     * lang.String, java.lang.String, gr.grnet.escience.fs.pithos.PithosBlock)
     */
    @Override
    public String appendPithosBlock(String pithosContainer,
            String targetObject, PithosBlock newPithosBlock) {

        // - Create Pithos request
        setPithosRequest(new PithosRequest());

        // - Request Parameters
        getPithosRequest().getRequestParameters().put("format", "json");

        // - Request Headers
        getPithosRequest().getRequestHeaders().put("Content-Type",
                "application/octet-stream");

        getPithosRequest().getRequestHeaders()
                .put("Content-Range", "bytes */*");

        contentLength = ((Integer) newPithosBlock.getBlockData().length)
                .toString();

        getPithosRequest().getRequestHeaders().put("Content-Length",
                contentLength);

        getPithosRequest().getRequestHeaders().put("Content-Encoding", "UTF-8");

        try {
            encString = Base64.getEncoder().encodeToString(
                    newPithosBlock.getBlockData());
            return update_append_truncate_object(pithosContainer, targetObject,
                    encString, getPithosRequest().getRequestParameters(),
                    getPithosRequest().getRequestHeaders());
        } catch (UnsupportedEncodingException e) {
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        } catch (IOException e) {
            // - Return the exception message as String
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        }

    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#retrievePithosBlocks(java
     * .lang.String, java.lang.String, long, long)
     */
    @Override
    public File retrievePithosBlocks(String pithosContainer,
            String targetObject, long targetBlockStart, long targetBlockEnd) {

        setPithosRequest(new PithosRequest());

        // - Request Parameters
        // - JSON Format
        getPithosRequest().getRequestParameters().put("format", "json");
        // - Add requested parameter for the range
        // - If it is not requested the last block, then add specific range
        getPithosRequest().getRequestHeaders().put("Range",
                "bytes=" + targetBlockStart + "-" + targetBlockEnd);

        // - Read data object
        try {
            // - Get the chunk of the pithos object as a file
            blockData = (File) read_object_data(targetObject, pithosContainer,
                    getPithosRequest().getRequestParameters(),
                    getPithosRequest().getRequestHeaders());

            // - Return the created pithos object
            return blockData;
        } catch (IOException e) {
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#storePithosBlock(java.lang
     * .String, java.lang.String, gr.grnet.escience.fs.pithos.PithosBlock,
     * java.io.File)
     */
    @Override
    public String storePithosBlock(String pithosContainer, String targetObject,
            PithosBlock pithosBlock, File backupFile) {
        return null;
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#pithosObjectOutputStream
     * (java.lang.String, java.lang.String,
     * gr.grnet.escience.fs.pithos.PithosObject)
     */
    @Override
    public String pithosObjectOutputStream(String pithosContainer,
            String objectName, PithosObject pithosObject) {
        return null;
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * gr.grnet.escience.fs.pithos.PithosSystemStore#pithosBlockOutputStream
     * (java.lang.String, java.lang.String,
     * gr.grnet.escience.fs.pithos.PithosBlock)
     */
    @Override
    public String pithosBlockOutputStream(String pithosContainer,
            String targetObject, PithosBlock pithosBlock) {
        return null;
    }

}
