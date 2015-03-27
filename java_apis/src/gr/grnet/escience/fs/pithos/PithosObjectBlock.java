package gr.grnet.escience.fs.pithos;


public class PithosObjectBlock {
  private String blockHash;
  private long blockLength;
  private byte[] blockData;
  
  public PithosObjectBlock(String _blockHash, long _blockLength, byte [] _blockData) {
    this.blockHash = _blockHash;
    this.blockLength = _blockLength;
    this.blockData = _blockData;
  }

  public String getBlockHash() {
    return blockHash;
  }

  public long getBlockLength() {
    return blockLength;
  }

  public byte[] getBlockData(){
	  return blockData;
  }
  
  @Override
  public String toString() {
    return "ObjectBlock[" + getBlockHash() + ", " + getBlockLength() + "]";
  }

}
