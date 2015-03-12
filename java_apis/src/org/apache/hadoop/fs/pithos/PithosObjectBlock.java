package org.apache.hadoop.fs.pithos;


public class PithosObjectBlock {
  private long blockHash;

  private long blockLength;

  public PithosObjectBlock(long _blockHash, long _blockLength) {
    this.blockHash = _blockHash;
    this.blockLength = _blockLength;
  }

  public long getBlockHash() {
    return blockHash;
  }

  public long getBlockLength() {
    return blockLength;
  }

  @Override
  public String toString() {
    return "ObjectBlock[" + getBlockHash() + ", " + getBlockLength() + "]";
  }

}
