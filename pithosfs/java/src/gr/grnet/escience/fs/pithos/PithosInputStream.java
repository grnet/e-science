package gr.grnet.escience.fs.pithos;

import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectOutput;
import java.io.ObjectOutputStream;
import java.util.ArrayList;
import java.util.Collection;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.fs.FSInputStream;
import org.apache.hadoop.fs.FileSystem;

/**
 * This class implements the FSInputstream by extending Hadoop 2.6.0 API native
 * FSInputStream class The class has been structured by taking into account the
 * structure of the corresponding one in the Amazon S3 API
 * 
 * @since March, 2015
 * @author Dimitris G. Kelaidonis (kelaidonis@gmail.com) & Ioannis Stenos
 *         (johnstenos83@gmail.com)
 * @version 0.1
 * 
 */
public class PithosInputStream extends FSInputStream {

	private boolean closed;
	
	private long fileLength;

	private long pos = 0;

	private File blockFile;
	
	private long pithosBlockNum;

	private DataInputStream blockStream;

	private String _pithos_container;

	private String _pithos_object;
	
	private String currentBlockHash;

	private long blockEnd = -1;

	private FileSystem.Statistics stats;
	
	private Collection<String> blockHashesList = new ArrayList<String>(); 
	
	private Object[] blockHashesArray;

	private static final Log LOG = LogFactory.getLog(PithosInputStream.class
			.getName());

	// private static final String TEST_FILE_FROM_PITHOS = "server.txt";

	public PithosInputStream() {
	}

	public PithosInputStream(String pithos_container, String pithos_object) {

		// - Initialize local variables
		this._pithos_container = pithos_container;
		this._pithos_object = pithos_object;
      
		// - Get Object Blocks
		this.blockHashesList = PithosFileSystem.getHadoopPithosConnector().getPithosObjectBlockHashes(getRequestedContainer(), getRequestedObject());
        
		this.setAvailableBlocksAsArray();
		
		this.pithosBlockNum = PithosFileSystem.getHadoopPithosConnector().getPithosObjectBlocksNumber(getRequestedContainer(), getRequestedObject());
		this.fileLength = PithosFileSystem.getHadoopPithosConnector().getPithosObjectSize(getRequestedContainer(), getRequestedObject());
	}
	
	private Collection<String> getAvailableBlocks() { 
		return blockHashesList;
	}

	private String getRequestedContainer() {
		return _pithos_container;
	}

	private String getRequestedObject() {
		return _pithos_object;
	}

	private long getPithosObjectBlockNum() {
		return pithosBlockNum;
	}
	
	private void setAvailableBlocksAsArray(){
		blockHashesArray = getAvailableBlocks().toArray();		
	}
	
	private Object[] getAvailableBlocksAsArray(){
		return blockHashesArray;
	}
	
	private synchronized void blockSeekTo(long target) throws IOException {
		int targetBlock = -1;
		long targetBlockStart = 0;
		long targetBlockEnd = 0;
        int i = 0; 
        int l = 0;
        PithosBlock [] p_file_block = new PithosBlock[32];
        
        long HadoopBlockLen = 0;
		
		while (getAvailableBlocks().iterator().hasNext()) {
			
			currentBlockHash = getAvailableBlocks().iterator().next();
			
			
			long blockLength = PithosFileSystem.getHadoopPithosConnector()
			.retrievePithosBlock(getRequestedContainer(),
					getRequestedObject(), currentBlockHash).getBlockLength();
			targetBlockEnd = targetBlockStart + blockLength - 1;

			if (target >= targetBlockStart && target <= targetBlockEnd) {
				targetBlock = i;
				if (targetBlock + 32 < getPithosObjectBlockNum() ){
					for (int k=targetBlock; k<targetBlock+32; k++){
						
						p_file_block[l] = PithosFileSystem.getHadoopPithosConnector()
								.retrievePithosBlock(getRequestedContainer(),
										getRequestedObject(),
										getAvailableBlocksAsArray()[k].toString());
						HadoopBlockLen = HadoopBlockLen + p_file_block[l].getBlockLength();
						l++;
					}
				}
				else {
                    for (int k=targetBlock; k<getPithosObjectBlockNum(); k++){ 
						p_file_block[l] = PithosFileSystem.getHadoopPithosConnector()
								.retrievePithosBlock(getRequestedContainer(),
										getRequestedObject(),
										getAvailableBlocksAsArray()[k].toString());
						HadoopBlockLen = HadoopBlockLen + p_file_block[l].getBlockLength();
						l++;
					}
				}
				targetBlockEnd = targetBlockStart + HadoopBlockLen - 1;
				break;
			} else {
				targetBlockStart = targetBlockEnd + 1;
			}
			i++; 
		}
		if (targetBlock < 0) {
			throw new IOException(
					"Impossible situation: could not find target position "
							+ target);
		}
		long offsetIntoBlock = target - targetBlockStart;

		// - Read block blocks[targetBlock] from position offsetIntoBlock

		// - Create block file	
		this.blockFile = retrieveBlock(p_file_block, offsetIntoBlock);

		this.pos = target;
		this.blockEnd = targetBlockEnd;
		this.blockStream = new DataInputStream(new FileInputStream(blockFile));

	}
    private synchronized File retrieveBlock(PithosBlock[] pithosobjectblock, long offsetIntoBlock) throws IOException{
		
		ByteArrayOutputStream bos = new ByteArrayOutputStream();
		ObjectOutput out = null;
		FileOutputStream fileOutputStream = null;
		long block_len = 0;
		try {
		  out = new ObjectOutputStream(bos);
		  for (int i=0; i< pithosobjectblock.length; i++){
			  if (pithosobjectblock[i] != null){
		           out.writeObject(pithosobjectblock[i].getBlockData());
		           block_len = block_len + pithosobjectblock[i].getBlockLength();
			  }
			  else {
				  //end of array of pithos blocks
				  break;
			  }
		  }
		  byte[] yourBytes = bos.toByteArray();
		  
		  
		  Integer offset = (int)(long)offsetIntoBlock;
		  Integer blocklenMinusoffset = (int)(long)(block_len - offsetIntoBlock);
		  
		  File block = new File("/tmp/blockfile");
		  if (!block.exists()) {
				block.createNewFile();
			}
			// - Create output stream with data to the file
			fileOutputStream = new FileOutputStream(block);
			fileOutputStream.write(yourBytes, offset, blocklenMinusoffset);
			fileOutputStream.flush();
			fileOutputStream.close();
			//fileOuputStream.close();
			// - return the file
			return block;

		} finally {
		  try {
		    if (out != null) {
		      out.close();
		      
		    }
		  } catch (IOException ex) {
		    // ignore close exception
		  }
		  try {
		    bos.close();
		  } catch (IOException ex) {
		    // ignore close exception
		  }
		  try {
				if (fileOutputStream != null) {
					fileOutputStream.close();
				}
			} catch (IOException e) {
				// ignore close exception
			}
		}
		
		
	}
	@Override
	public synchronized long getPos() throws IOException {
		return pos;
	}

	@Override
	public synchronized int available() throws IOException {
		return (int) (fileLength - pos);
	}

	@Override
	public synchronized void seek(long targetPos) throws IOException {
		if (targetPos > fileLength) {
			throw new IOException("Cannot seek after EOF");
		}
		pos = targetPos;
		blockEnd = -1;
	}

	@Override
	public synchronized boolean seekToNewSource(long targetPos)
			throws IOException {
		return false;
	}

	@Override
	public synchronized int read() throws IOException {
		if (closed) {
			throw new IOException("Stream closed");
		}
		int result = -1;
		if (pos < fileLength) {
			if (pos > blockEnd) {
				blockSeekTo(pos);
			}
			result = blockStream.read();
			if (result >= 0) {
				pos++;
			}
		}
		if (stats != null && result >= 0) {
			stats.incrementBytesRead(1);
		}
		return result;
	}

	@Override
	public synchronized int read(byte buf[], int off, int len)
			throws IOException {
		if (closed) {
			throw new IOException("Stream closed");
		}
		if (pos < fileLength) {
			if (pos > blockEnd) {
				blockSeekTo(pos);
			}
			int realLen = (int) Math.min(len, (blockEnd - pos + 1L));
			int result = blockStream.read(buf, off, realLen);
			if (result >= 0) {
				pos += result;
			}
			if (stats != null && result > 0) {
				stats.incrementBytesRead(result);
			}
			return result;
		}
		return -1;
	}

	@Override
	public void close() throws IOException {
		if (closed) {
			return;
		}
		if (blockStream != null) {
			blockStream.close();
			blockStream = null;
		}
		if (blockFile != null) {
			boolean b = blockFile.delete();
			if (!b) {
				LOG.warn("Ignoring failed delete");
			}
		}
		super.close();
		closed = true;
	}

	@Override
	public boolean markSupported() {
		return false;
	}

	@Override
	public void mark(int readLimit) {
		// Do nothing
	}

	@Override
	public void reset() throws IOException {
		throw new IOException("Mark not supported");
	}

}
