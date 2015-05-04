package gr.grnet.escience.pithos.rest;

import java.util.Collection;

public class PithosResponseHashmap {
    private String block_hash;
    private String block_size;
    private String bytes;
    private Collection<String> hashes;

    /**
     * Object Hashes list
     */
    public Collection<String> getBlockHashes() {
        return hashes;
    }

    public void setBlockHashes(Collection<String> hashes) {
        this.hashes = hashes;
    }

    public String getBlockHash() {
        return block_hash;
    }

    public void setBlockHash(String block_hash) {
        this.block_hash = block_hash;
    }

    public String getBlockSize() {
        return block_size;
    }

    public void setBlockSize(String block_size) {
        this.block_size = block_size;
    }

    public String getObjectSize() {
        return bytes;
    }

    public void setObjectSize(String bytes) {
        this.bytes = bytes;
    }
}
