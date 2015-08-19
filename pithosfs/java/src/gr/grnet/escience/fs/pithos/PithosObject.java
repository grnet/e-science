package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.commons.Utils;

import java.io.BufferedInputStream;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInput;
import java.io.ObjectInputStream;
import java.io.Serializable;
import gr.grnet.escience.commons.Utils;

/**
 * Stores pithos object information.
 */
public class PithosObject implements Serializable {

    private static final long serialVersionUID = 1L;
    
    private transient PithosBlock[] objectBlocks = null;
    
    private String objectName = null;
    
    private long totalSize = -1;
    
    private transient ByteArrayOutputStream bytes = null;
    
    private transient DataOutputStream out = null;
    
    private transient ByteArrayInputStream serializedInputStream = null;
    
    private static InputStream buffer = null;
    
    private static ObjectInput input = null;

    /**
     *  Create a Pithos Object *.
     *
     * @param name : object name - String
     * @param blocks : PithosBlock array
     */
    public PithosObject(String name, PithosBlock[] blocks) {
        // - Initialize object name & blocks of the object
        this.objectName = name;
        this.objectBlocks = blocks;
    }

    /**
     *  Create a Pithos Object *.
     *
     * @param path the path
     * @param blocks the blocks
     */
    public PithosObject(PithosPath path, PithosBlock[] blocks) {
        // - Extract Object Absolute Name by excluding Scheme & container
        this.objectName = path.getObjectName();
        this.objectBlocks = blocks;
    }

    public String getName() {
        return objectName;
    }

    public PithosBlock[] getBlocks() {
        return objectBlocks;
    }

    public int getBlocksNumber() {
        // - Check if there are available blocks
        if (getBlocks() == null) {
            return getBlocks().length;
        } else {
            return 0;
        }

    }

    /**
     * Gets the object size.
     *
     * @return totalSize: the total object size in Bytes
     */
    public long getObjectSize() {
        // - Check if there are available blocks
        if (getBlocks() != null) {
            totalSize = 0;

            // - Iterate on all available objects and get the total size in
            // bytes
            for (PithosBlock currentBlock : getBlocks()) {
                totalSize += currentBlock.getBlockLength();
            }
        }
        // - return total size
        return totalSize;
    }

    /**
     * Serialize a Pithos Object so as to perform various actions, such as to
     * copy it to the pithos FS.
     *
     * @return the input stream
     * @throws IOException : Failure to write to OutputStream
     */
    public InputStream serialize() throws IOException {
        // - Initialize parameters for stream
        bytes = new ByteArrayOutputStream();
        out = new DataOutputStream(bytes);
        serializedInputStream = null;

        if (getBlocksNumber() > 0) {
            try {
                // - Add object name
                out.write(getName().getBytes("UTF-8"));
                // - Add object blocks total number
                out.writeInt(getBlocksNumber());
                // - Add object size
                out.writeLong(getObjectSize());

                // - Add all available blocks for the object
                for (int i = 0; i < getBlocksNumber(); i++) {
                    out.write(getBlocks()[i].getBlockHash().getBytes("UTF-8"));
                    out.writeLong(getBlocks()[i].getBlockLength());
                    out.write(getBlocks()[i].getBlockData());
                }
            } finally {
                bytes.close();
                out.close();
                bytes = null;
                out = null;
            }
            // - return the inputstream
            serializedInputStream = new ByteArrayInputStream(
                    bytes.toByteArray());

            return serializedInputStream;
        } else {
            return null;
        }

    }

    /**
     * *
     * Deserialize a Pithos Object that is received from the pithos FS.
     *
     * @param inputStreamForObject the input stream for object
     * @return the pithos object
     */
    public static PithosObject deserialize(InputStream inputStreamForObject) {
        if (inputStreamForObject == null) {
            return null;
        }

        buffer = new BufferedInputStream(inputStreamForObject);
        input = null;

        try {
            input = new ObjectInputStream(buffer);
            return (PithosObject) input.readObject();
        } catch (ClassNotFoundException | IOException e) {
            Utils.dbgPrint(e.getMessage(), e);
            return null;
        } finally {
            try {
                buffer.close();
                input.close();
                buffer = null;
                input = null;
            } catch (IOException e) {
                buffer = null;
                input = null;
                Utils.dbgPrint(e.getMessage(), e);
            }

        }
    }

}
