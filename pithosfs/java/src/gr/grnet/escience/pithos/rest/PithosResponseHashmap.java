package gr.grnet.escience.pithos.rest;

import java.util.Collection;

/**
 * Used for serializing a json object into a java object.
 */
public class PithosResponseHashmap {

    private String blockHash;

    private String blockSize;

    private String bytes;

    private Collection<String> hashes;

    public Collection<String> getBlockHashes() {
        return hashes;
    }

    public void setBlockHashes(Collection<String> hashes) {
        this.hashes = hashes;
    }

    public String getBlockHash() {
        return blockHash;
    }

    public void setBlockHash(String blockHash) {
        this.blockHash = blockHash;
    }

    public String getBlockSize() {
        return blockSize;
    }

    public void setBlockSize(String blockSize) {
        this.blockSize = blockSize;
    }

    public String getObjectSize() {
        return bytes;
    }

    public void setObjectSize(String bytes) {
        this.bytes = bytes;
    }
}
