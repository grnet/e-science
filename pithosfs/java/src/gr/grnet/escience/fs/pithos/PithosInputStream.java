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
import org.apache.hadoop.mapreduce.Job;

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
    private static final long DEFAULT_BLOCK_SIZE = (long) 128 * 1024 * 1024;
    private long pithosContainerBlockSize = 0;
    private int result = -1;
    private Configuration conf = new Configuration();

    public PithosInputStream() {
    }

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

    private void setHadoopToPithosBlock() {
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

    @Override
    public void close() throws IOException {
        if (closed) {
            Job.getInstance().killJob();
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
        Job.getInstance().killJob();
        throw new IOException("Mark not supported");
    }

}
