package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.commons.Utils;

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
 * Implements the PithosInputStream by extending Hadoop 2.5.2 API native
 * FSInputStream class. The class was initially modeled after the Amazon S3
 * implementation.
 *
 * @author Dimitris G. Kelaidonis (kelaidonis@gmail.com) and Ioannis Stenos
 *         (johnstenos83@gmail.com)
 * @version 0.1
 * @since March, 2015
 */
public class PithosInputStream extends FSInputStream {

    private int hadoopToPithosBlock = 0;

    private boolean closed = false;

    private long fileLength = 0;

    private long pos = 0;

    private File blockFile = null;

    private DataInputStream blockStream = null;

    private String pithosContainer = null;

    private String pithosObject = null;

    private long blockEnd = -1;

    private FileSystem.Statistics stats = null;

    private static final Log LOG = LogFactory.getLog(FSInputStream.class
            .getName());

    private static final long HDFS_DEFAULT_BLOCK_SIZE = (long) 128 * 1024 * 1024;

    /**
     * The pithos container block size. Value is updated through pithos
     * connector call.
     */
    private long pithosContainerBlockSize = (long) 4 * 1024 * 1024;

    private int result = -1;

    private Configuration conf = new Configuration();

    /**
     * Instantiates a new pithos input stream.
     */
    public PithosInputStream() {
    }

    /**
     * Instantiates a new pithos input stream.
     *
     * @param pithosContainerIn
     *            : pithos container as String
     * @param pithosObjectIn
     *            : pithos object name as String
     */
    public PithosInputStream(String pithosContainerIn, String pithosObjectIn) {
        // - Initialize local variables
        this.pithosContainer = pithosContainerIn;
        this.pithosObject = pithosObjectIn;
        this.pithosContainerBlockSize = PithosFileSystem
                .getHadoopPithosConnector().getPithosBlockDefaultSize(
                        getRequestedContainer());

        this.setHadoopToPithosBlock();

        // - Get Object Length
        this.fileLength = PithosFileSystem.getHadoopPithosConnector()
                .getPithosObjectSize(getRequestedContainer(),
                        getRequestedObject());
    }

    private int getHadoopToPithosBlock() {
        return hadoopToPithosBlock;
    }

    private long getPithosContainerBlockSize() {
        return pithosContainerBlockSize;
    }

    /**
     * Calculates HDFS blocksize to pithos container blocksize ratio.
     */
    private void setHadoopToPithosBlock() {
        this.hadoopToPithosBlock = (int) (conf.getLongBytes("dfs.blocksize",
                HDFS_DEFAULT_BLOCK_SIZE) / getPithosContainerBlockSize());
    }

    private String getRequestedContainer() {
        return pithosContainer;
    }

    private String getRequestedObject() {
        return pithosObject;
    }

    /**
     * Seeks to target in block.
     *
     * @param target
     *            : target byte
     * @throws IOException
     *             : failed to read the blockFile.
     */
    private synchronized void blockSeekTo(long target) throws IOException {

        long targetBlockEnd = 0;

        long sizeOfPithosBlocksToRead = getHadoopToPithosBlock()
                * getPithosContainerBlockSize();

        if (target + sizeOfPithosBlocksToRead <= fileLength) {
            targetBlockEnd = target + sizeOfPithosBlocksToRead - 1;
        } else {
            targetBlockEnd = fileLength - 1;
        }

        this.blockFile = PithosFileSystem.getHadoopPithosConnector()
                .retrievePithosBlocks(getRequestedContainer(),
                        getRequestedObject(), target, targetBlockEnd);
        this.pos = target;
        this.blockEnd = targetBlockEnd;
        this.blockStream = new DataInputStream(new FileInputStream(blockFile));

    }

    /*
     * (non-Javadoc)
     * 
     * @see org.apache.hadoop.fs.FSInputStream#getPos()
     */
    @Override
    public synchronized long getPos() throws IOException {
        return pos;
    }

    /*
     * (non-Javadoc)
     * 
     * @see java.io.InputStream#available()
     */
    @Override
    public synchronized int available() throws IOException {
        return (int) (fileLength - pos);
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.apache.hadoop.fs.FSInputStream#seek(long)
     */
    @Override
    public synchronized void seek(long targetPos) throws IOException {
        if (targetPos > fileLength) {
            Utils.dbgPrint("Cannot seek after EOF");
            throw new IOException("Cannot seek after EOF");
        }
        pos = targetPos;
        blockEnd = -1;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.apache.hadoop.fs.FSInputStream#seekToNewSource(long)
     */
    @Override
    public synchronized boolean seekToNewSource(long targetPos)
            throws IOException {
        return false;
    }

    /*
     * (non-Javadoc)
     * 
     * @see java.io.InputStream#read()
     */
    @Override
    public synchronized int read() throws IOException {
        if (closed) {
            throw new IOException("Stream closed");
        }
        result = -1;
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

    /*
     * (non-Javadoc)
     * 
     * @see java.io.InputStream#read(byte[], int, int)
     */
    @Override
    public synchronized int read(byte[] buf, int off, int len)
            throws IOException {
        if (closed) {
            Utils.dbgPrint("Stream closed");
            throw new IOException("Stream closed");
        }
        if (pos < fileLength) {
            if (pos > blockEnd) {
                blockSeekTo(pos);
            }
            int realLen = (int) Math.min(len, blockEnd - pos + 1L);
            int iresult = blockStream.read(buf, off, realLen);
            if (iresult >= 0) {
                pos += iresult;
            }
            if (stats != null && iresult > 0) {
                stats.incrementBytesRead(iresult);
            }
            return iresult;
        }
        return -1;
    }

    /*
     * (non-Javadoc)
     * 
     * @see java.io.InputStream#close()
     */
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

    /*
     * (non-Javadoc)
     * 
     * @see java.io.InputStream#markSupported()
     */
    @Override
    public boolean markSupported() {
        return false;
    }

    /*
     * (non-Javadoc)
     * 
     * @see java.io.InputStream#mark(int)
     */
    @Override
    public void mark(int readLimit) {
        // Do nothing
    }

    /*
     * (non-Javadoc)
     * 
     * @see java.io.InputStream#reset()
     */
    @Override
    public void reset() throws IOException {
        Utils.dbgPrint("Mark not supported");
        throw new IOException("Mark not supported");
    }

}
