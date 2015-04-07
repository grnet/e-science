package gr.grnet.escience.fs.pithos;

import java.io.IOException;
import java.io.OutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem.Statistics;

/**
 * Wraps FSDataOutputStream (which wraps OutputStream) for streaming data into Pithos
 */
public class PithosOutputStream extends FSDataOutputStream {
	/**
	 * Hadoop configuration
	 */
	private Configuration conf;

	/**
	 * buffer size
	 */
	private int bufferSize;

	/**
	 * FS store instance
	 */
	private PithosSystemStore store;

	/**
	 * Destination path
	 */
	private PithosPath path;

	/**
	 * size of block
	 */
	private long blockSize;

	/**
	 * backup where data is writing before streaming in pithos
	 */
	private File backupFile;

	/**
	 * output stream
	 */
	private OutputStream backupStream;

	/**
	 * random for generating next id for block
	 */
	private Random r = new Random();

	/**
	 * flag if stream closed
	 */
	private boolean closed;

	/**
	 * current position
	 */
	private int pos = 0;

	/**
	 * file position
	 */
	private long filePos = 0;

	/**
	 * written bytes
	 */
	private int bytesWrittenToBlock = 0;

	/**
	 * output buffer
	 */
	private byte[] outBuf;

	/**
	 * blocks of file
	 */
	private List<PithosBlock> blocks = new ArrayList<PithosBlock>();

	/**
	 * current block to store to pithos
	 */
	private PithosBlock nextBlock;

	/**
	 * method for creating backup file of 4mb for buffering
	 * before streaming to pithos
	 * 
	 * @return File
	 * @throws IOException
	 */
	private File newBackupFile() throws IOException {
		File dir = new File(conf.get("hadoop.tmp.dir"));
		if (!dir.exists() && !dir.mkdirs()) {
			throw new IOException("Cannot create pithos buffer directory: "
					+ dir);
		}
		File result = File.createTempFile("output-", ".tmp", dir);
		result.deleteOnExit();
		return result;
	}

	public long getPos() throws IOException {
		return filePos;
	}

	@Override
	public synchronized void write(int b) throws IOException {
		if (closed) {
			throw new IOException("Stream closed");
		}

		if ((bytesWrittenToBlock + pos == blockSize) || (pos >= bufferSize)) {
			flush();
		}
		outBuf[pos++] = (byte) b;
		filePos++;
	}

	@Override
	public synchronized void write(byte b[], int off, int len)
			throws IOException {
		if (closed) {
			throw new IOException("Stream closed");
		}
		while (len > 0) {
			int remaining = bufferSize - pos;
			int toWrite = Math.min(remaining, len);
			System.arraycopy(b, off, outBuf, pos, toWrite);
			pos += toWrite;
			off += toWrite;
			len -= toWrite;
			filePos += toWrite;

			if ((bytesWrittenToBlock + pos >= blockSize) || (pos == bufferSize)) {
				flush();
			}
		}
	}

	@Override
	public synchronized void flush() throws IOException {
		if (closed) {
			throw new IOException("Stream closed");
		}

		if (bytesWrittenToBlock + pos >= blockSize) {
			flushData((int) blockSize - bytesWrittenToBlock);
		}
		if (bytesWrittenToBlock == blockSize) {
			endBlock();
		}
		flushData(pos);
	}

	/**
	 * Flushes data to output buffer
	 * 
	 * @param maxPos
	 *            position to which backup data
	 * @throws IOException
	 */
	private synchronized void flushData(int maxPos) throws IOException {
		int workingPos = Math.min(pos, maxPos);

		if (workingPos > 0) {
			//
			// To the local block backup, write just the bytes
			//
			backupStream.write(outBuf, 0, workingPos);

			//
			// Track position
			//
			bytesWrittenToBlock += workingPos;
			System.arraycopy(outBuf, workingPos, outBuf, 0, pos - workingPos);
			pos -= workingPos;
		}
	}

	/**
	 * Stores block in pithos
	 * 
	 * @throws IOException
	 */
	private synchronized void endBlock() throws IOException {
		//
		// Done with local copy
		//
		backupStream.close();

		//
		// Send it to pithos
		String pithos_container = "pithos"; //TODO: get from destination path
		String target_object = "test_out";
		nextBlockOutputStream();
		store.storePithosBlock(pithos_container,target_object, nextBlock, backupFile);
//		internalClose();

		//
		// Delete local backup, start new one
		//
		backupFile.delete();
		backupFile = newBackupFile();
		backupStream = new FileOutputStream(backupFile);
		bytesWrittenToBlock = 0;
	}

	/**
	 * Creates next block for output stream
	 * 
	 * @throws IOException
	 */
	private synchronized void nextBlockOutputStream() throws IOException {
		long blockId = r.nextLong();
		String strBlock = Long.toString(blockId); // TODO: Refactor to pithos block hash check / generation
		while (store.pithosObjectBlockExists(strBlock)) {
			blockId = r.nextLong();
		}
		byte[] blockData = null; // TODO: serialize the buffer file
		nextBlock = new PithosBlock(strBlock, bytesWrittenToBlock, blockData);
		blocks.add(nextBlock);
		bytesWrittenToBlock = 0;
	}

//	/**
//	 * Close and save all information carefully on internal close
//	 * 
//	 * @throws IOException
//	 */
//	private synchronized void internalClose() throws IOException {
//		INode inode = new INode(INode.FILE_TYPES[1],
//				blocks.toArray(new Block[blocks.size()]));
//		store.storeINode(path, inode);
//	}

	@Override
	public synchronized void close() throws IOException {
		if (closed) {
			return;
		}

		flush();
		if (filePos == 0 || bytesWrittenToBlock != 0) {
			endBlock();
		}

		backupStream.close();
		backupFile.delete();

		super.close();

		closed = true;
	}

	/**
	 * @param conf
	 *            FS conf
	 * @param store
	 *            FS store
	 * @param path
	 *            file path
	 * @param blockSize
	 *            size of block
	 * @param buffersize
	 *            size of buffer
	 * @throws IOException
	 */
	public PithosOutputStream(OutputStream out, Statistics stats,
			Configuration conf, PithosSystemStore store, PithosPath path,
			long blockSize, int buffersize) throws IOException {
		super(out, stats);
		this.conf = conf;
		this.store = store;
		this.path = path;
		this.blockSize = blockSize;
		this.backupFile = newBackupFile();
		this.backupStream = new FileOutputStream(backupFile);
		this.bufferSize = buffersize;
		this.outBuf = new byte[bufferSize];
	}
}
