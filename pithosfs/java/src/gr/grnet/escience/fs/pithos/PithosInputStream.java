package gr.grnet.escience.fs.pithos;

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
    
    private int hadoopToPithosBlock = 0;

    private boolean closed;

    private long fileLength;

    private long pos = 0;

    private File blockFile;

    private DataInputStream blockStream;

    private String pithosContainer;

    private String pithosObject;

    private long blockEnd = -1;

    private FileSystem.Statistics stats;

    private static final Log LOG = LogFactory.getLog(FSInputStream.class
            .getName());

    private static final long DEFAULT_BLOCK_SIZE = (long) 128 * 1024 * 1024;

    private long pithosContainerBlockSize = 0;

    public PithosInputStream() {
    }

    public PithosInputStream(String pithosContainer, String pithosObject) {

        // - Initialize local variables
        this.pithosContainer = pithosContainer;
        this.pithosObject = pithosObject;
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

    private void setHadoopToPithosBlock() {
        Configuration conf = new Configuration();

        this.hadoopToPithosBlock = (int) (conf.getLongBytes("dfs.blocksize",
                DEFAULT_BLOCK_SIZE) / getPithosContainerBlockSize());

    }

    private String getRequestedContainer() {
        return pithosContainer;
    }

    private String getRequestedObject() {
        return pithosObject;
    }

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
    public synchronized int read(byte[] buf, int off, int len)
            throws IOException {
        if (closed) {
            throw new IOException("Stream closed");
        }
        if (pos < fileLength) {
            if (pos > blockEnd) {
                blockSeekTo(pos);
            }
            int realLen = (int) Math.min(len, blockEnd - pos + 1L);
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
