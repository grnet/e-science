package gr.grnet.escience.fs.pithos;

import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSInputStream;
import org.apache.hadoop.fs.FileSystem;

/**
 * This class implements the FSInputstream by extending Hadoop 2.5.2 API native
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

	private int HadoopToPithosBlock = 0;

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

	private static final long defaultBlockSize = (long) 128 * 1024 * 1024;

	private PithosBlock[] pithosToHadoopBlocks = null;

	private long HadoopBlockLen = 0;

	public PithosInputStream() {
	}

	public PithosInputStream(String pithos_container, String pithos_object) {

		// - Initialize local variables
		this._pithos_container = pithos_container;
		this._pithos_object = pithos_object;
		this.setHadoopToPithosBlock();
		// - Get Object Blocks
		this.blockHashesList = PithosFileSystem.getHadoopPithosConnector()
				.getPithosObjectBlockHashes(getRequestedContainer(),
						getRequestedObject());
		// - Set Collection of BlockHashes as an array of BlockHashes
		this.pithosToHadoopBlocks = new PithosBlock[getHadoopToPithosBlock()];

		this.setAvailableBlocksAsArray();
		// - Get Number of Pithos Object Blocks
		this.pithosBlockNum = PithosFileSystem.getHadoopPithosConnector()
				.getPithosObjectBlocksNumber(getRequestedContainer(),
						getRequestedObject());
		// - Get Object Length
		this.fileLength = PithosFileSystem.getHadoopPithosConnector()
				.getPithosObjectSize(getRequestedContainer(),
						getRequestedObject());
	}

	private Collection<String> getAvailableBlocks() {
		return blockHashesList;
	}

	private int getHadoopToPithosBlock() {
		return HadoopToPithosBlock;
	}

	private void setHadoopToPithosBlock() {
		Configuration conf = new Configuration();

		this.HadoopToPithosBlock = (int) (conf.getLongBytes("dfs.blocksize",
				defaultBlockSize) / PithosFileSystem.getHadoopPithosConnector()
				.getPithosBlockDefaultSize(getRequestedContainer()));

	}

	private void setPithosToHadoopBlocks(int index, PithosBlock element) {
		pithosToHadoopBlocks[index] = element;
	}

	private PithosBlock getPithosToHadoopBlocks(int index) {
		return pithosToHadoopBlocks[index];
	}

	private PithosBlock[] getPithosToHadoopArray() {
		return pithosToHadoopBlocks;
	}

	private void setHadoopBlockLen(long value) {
		HadoopBlockLen = value;
	}

	private long getHadoopBlockLen() {
		return HadoopBlockLen;
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

	private void setAvailableBlocksAsArray() {
		blockHashesArray = getAvailableBlocks().toArray();
	}

	private Object[] getAvailableBlocksAsArray() {
		return blockHashesArray;
	}

	private synchronized void blockSeekTo(long target) throws IOException {
		int targetBlock = -1;
		long targetBlockStart = 0;
		long targetBlockEnd = 0;
		int i = 0;
		// -Used for iterations and index in arrays.
		int pithosBlocksToHadoopBlockIndex = 0;
		int pithosBlocksIndex = 0;

		while (getAvailableBlocks().iterator().hasNext()) {

			currentBlockHash = getAvailableBlocks().iterator().next();

			long blockLength = PithosFileSystem
					.getHadoopPithosConnector()
					.retrievePithosBlock(getRequestedContainer(),
							getRequestedObject(), currentBlockHash)
					.getBlockLength();
			targetBlockEnd = targetBlockStart + blockLength - 1;

			if (target >= targetBlockStart && target <= targetBlockEnd) {
				targetBlock = i;
				long stop = -1;
				// -
				if (targetBlock + getHadoopToPithosBlock() < getPithosObjectBlockNum()) {
					stop = targetBlock + getHadoopToPithosBlock();
				} else {
					stop = getPithosObjectBlockNum();
				}

				// - Check if targetblock plus 32 (default for now, number of
				// pithos blocks to one hadoop block) is
				// not over the number of pithos object blocks
				// if (targetBlock + getHadoopToPithosBlock() <
				// getPithosObjectBlockNum()) {

				// for (pithosBlocksIndex = targetBlock; pithosBlocksIndex <
				// targetBlock
				// + getHadoopToPithosBlock(); pithosBlocksIndex++) {
				for (pithosBlocksIndex = targetBlock; pithosBlocksIndex < stop; pithosBlocksIndex++) {
					setPithosToHadoopBlocks(
							pithosBlocksToHadoopBlockIndex,
							PithosFileSystem
									.getHadoopPithosConnector()
									.retrievePithosBlock(
											getRequestedContainer(),
											getRequestedObject(),
											getAvailableBlocksAsArray()[pithosBlocksIndex]
													.toString()));
					setHadoopBlockLen(getHadoopBlockLen()
							+ getPithosToHadoopBlocks(
									pithosBlocksToHadoopBlockIndex)
									.getBlockLength());
					pithosBlocksToHadoopBlockIndex++;
				}
				// } else {
				// for (pithosBlocksIndex = targetBlock; pithosBlocksIndex <
				// getPithosObjectBlockNum(); pithosBlocksIndex++) {
				// setPithosToHadoopBlocks(
				// pithosBlocksToHadoopBlockIndex,
				// PithosFileSystem
				// .getHadoopPithosConnector()
				// .retrievePithosBlock(
				// getRequestedContainer(),
				// getRequestedObject(),
				// getAvailableBlocksAsArray()[pithosBlocksIndex]
				// .toString()));
				// setHadoopBlockLen(getHadoopBlockLen()
				// + getPithosToHadoopBlocks(
				// pithosBlocksToHadoopBlockIndex)
				// .getBlockLength());
				// pithosBlocksToHadoopBlockIndex++;
				// }
				// }
				targetBlockEnd = targetBlockStart + getHadoopBlockLen() - 1;
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
		this.blockFile = PithosFileSystem.getHadoopPithosConnector()
				.retrieveBlock(getPithosToHadoopArray(), offsetIntoBlock);

		this.pos = target;
		this.blockEnd = targetBlockEnd;
		this.blockStream = new DataInputStream(new FileInputStream(blockFile));

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
