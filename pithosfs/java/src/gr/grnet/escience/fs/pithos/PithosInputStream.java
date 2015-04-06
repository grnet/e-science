package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.pithos.rest.HadoopPithosConnector;

import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSInputStream;
import org.apache.hadoop.fs.FileSystem;

/**
 * This class implements the FSInputstream by extending Hadoop 2.6.0 API native
 * FSInputStream class The class has been structured by taking into account the
 * structure of the corresponding one in the Amazon S3 API
 * 
 * @since March, 2015
 * @author Dimitris G. Kelaidonis (kelaidonis@gmail.com)
 * @version 0.1
 * 
 */
public class PithosInputStream extends FSInputStream {

	// private PithosSystemStore store;

	private PithosBlock[] blocks;

	private HadoopPithosConnector pithos_conn;

	private boolean closed;

	private long fileLength;

	private long pos = 0;

	private File blockFile;

	private DataInputStream blockStream;

	private long blockEnd = -1;

	private FileSystem.Statistics stats;

	private static final Log LOG = LogFactory.getLog(PithosInputStream.class
			.getName());

	private static final String TEST_FILE_FROM_PITHOS = "server.txt";

	public PithosInputStream(HadoopPithosConnector pithos_conn) {
		this.pithos_conn = pithos_conn;

		this.blocks = this.pithos_conn.retrievePithosObjectBlocks("",
				TEST_FILE_FROM_PITHOS);
		for (PithosBlock block : blocks) {
			this.fileLength += block.getBlockLength();
		}
	}

	public PithosInputStream(Configuration conf, PithosSystemStore pithosStore,
			PithosObject pithosObj, FileSystem.Statistics stats) {

		// this.store = pithosStore;
		this.stats = stats;
		this.blocks = pithosObj.getPithosObjectBlocks();

		for (PithosBlock block : blocks) {
			this.fileLength += block.getBlockLength();
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

	private synchronized void blockSeekTo(long target) throws IOException {
		int targetBlock = -1;
		long targetBlockStart = 0;
		long targetBlockEnd = 0;

		for (int i = 0; i < blocks.length; i++) {
			long blockLength = blocks[i].getBlockLength();
			targetBlockEnd = targetBlockStart + blockLength - 1;

			if (target >= targetBlockStart && target <= targetBlockEnd) {
				targetBlock = i;
				break;
			} else {
				targetBlockStart = targetBlockEnd + 1;
			}
		}
		if (targetBlock < 0) {
			throw new IOException(
					"Impossible situation: could not find target position "
							+ target);
		}
		long offsetIntoBlock = target - targetBlockStart;

		// read block blocks[targetBlock] from position offsetIntoBlock

		PithosBlock p_file_block = this.pithos_conn.retrievePithosBlock("",
				"server.txt", blocks[targetBlock].getBlockHash());
		this.blockFile = pithos_conn.seekPithosBlock(p_file_block,
				offsetIntoBlock);

		this.pos = target;
		this.blockEnd = targetBlockEnd;
		this.blockStream = new DataInputStream(new FileInputStream(blockFile));

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
