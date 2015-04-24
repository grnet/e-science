package gr.grnet.escience.fs.pithos;

public class PithosBlock {
    private String blockHash;
    private long blockLength;
    private byte[] blockData;

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

    @Override
    public String toString() {
        return "ObjectBlock[" + getBlockHash() + ", " + getBlockLength() + "]";
    }

}
