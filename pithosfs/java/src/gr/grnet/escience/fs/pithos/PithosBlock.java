package gr.grnet.escience.fs.pithos;

/**
 * Stores pithos block information.
 */
public class PithosBlock {

    private String blockHash;

    private long blockLength;

    private byte[] blockData;

    /**
     * Instantiates a new pithos block.
     *
     * @param blockHash
     *            : the block hash as a string
     * @param blockLength
     *            : block length as int
     * @param blockData
     *            : the block data as byte array
     */
    public PithosBlock(String blockHash, long blockLength, byte[] blockData) {
        this.blockHash = blockHash;
        this.blockLength = blockLength;
        this.blockData = blockData;
    }

    public String getBlockHash() {
        return blockHash;
    }

    public long getBlockLength() {
        return blockLength;
    }

    public byte[] getBlockData() {
        return blockData;
    }

    /*
     * (non-Javadoc)
     * 
     * @see java.lang.Object#toString()
     */
    @Override
    public String toString() {
        return "ObjectBlock[" + getBlockHash() + ", " + getBlockLength() + "]";
    }

}
