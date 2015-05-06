package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.commons.PithosSerializer;
import gr.grnet.escience.commons.Utils;
import gr.grnet.escience.pithos.rest.HadoopPithosConnector;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;

import org.apache.hadoop.conf.Configuration;

/**
 * Wraps OutputStream for streaming data into Pithos
 */
public class PithosOutputStream extends OutputStream {

    private static String ERR_STREAM_CLOSED = "Stream closed";
    /**
     * Hadoop configuration
     */
    private Configuration conf;

    /**
     * buffer size
     */
    private int bufferSize;

    /**
     * Destination path
     */
    private PithosPath pithosPath;

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
     * Utils instance
     */
    private final Utils util = new Utils();

    /**
     * instance of HadoopPithosConnector
     */
    private HadoopPithosConnector hadoopConnector;

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
     * @param conf
     *            FS conf
     * @param path
     *            file path
     * @param blocksize
     *            size of block
     * @param buffersize
     *            size of buffer
     * @throws IOException
     */
    public PithosOutputStream(Configuration conf, PithosPath path,
            long blocksize, int buffersize) throws IOException {
        util.dbgPrint("PithosOutputStream ENTRY", path, blocksize, buffersize);
        this.conf = conf;
        this.pithosPath = path;
        this.blockSize = blocksize;
        this.hadoopConnector = new HadoopPithosConnector(
                conf.get("fs.pithos.url"), conf.get("auth.pithos.token"),
                conf.get("auth.pithos.uuid"));
        this.backupFile = newBackupFile();
        this.backupStream = new FileOutputStream(backupFile);
        this.bufferSize = buffersize;
        this.outBuf = new byte[buffersize];
        util.dbgPrint("PithosOutputStream EXIT");
    }

    /**
     * method for creating backup file of 4mb for buffering before streaming to
     * pithos
     * 
     * @return File
     * @throws IOException
     */
    private File newBackupFile() throws IOException {
        File dir = new File(conf.get("hadoop.tmp.dir"));
        util.dbgPrint("newBackupFile >", dir);
        if (!dir.exists() && !dir.mkdirs()) {
            throw new IOException(
                    "Cannot create local pithos buffer directory: " + dir);
        }
        File result = File.createTempFile("output-", ".tmp", dir);
        util.dbgPrint("newBackupFile > result:",result);
        result.deleteOnExit();
        return result;
    }

    public long getPos() throws IOException {
        return filePos;
    }

    @Override
    public synchronized void write(int b) throws IOException {
        util.dbgPrint("write(int)");
        if (closed) {
            throw new IOException(ERR_STREAM_CLOSED);
        }

        if ((bytesWrittenToBlock + pos == blockSize) || (pos >= bufferSize)) {
            flush();
        }
        outBuf[pos++] = (byte) b;
        filePos++;
    }

    @Override
    public synchronized void write(byte[] b, int off, int len)
            throws IOException {
        // util.dbgPrint("write(byte, int, int)",off,len);
        if (closed) {
            throw new IOException(ERR_STREAM_CLOSED);
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
        util.dbgPrint("flush");
        if (closed) {
            throw new IOException(ERR_STREAM_CLOSED);
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
        util.dbgPrint("flushData");
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
        util.dbgPrint("endBlock");
        //
        // Done with local copy
        //
        backupStream.close();
        //
        // Send it to pithos
        // String pithosContainer = pithosPath.getContainer();
        // String targetObject = pithosPath.getObjectAbsolutePath();
        // util.dbgPrint(pithosContainer, targetObject);
        // nextBlockOutputStream();

        // - Load file bytes
        byte[] endBlockData = PithosSerializer.serializeFile(backupFile);

        // - Create block and append on the existing object
        try {
            // - Create Pithos Block by using the content of the endBlock
            PithosBlock pithosBlock = new PithosBlock(util.computeHash(
                    endBlockData, "SHA-256"), endBlockData.length, endBlockData);

            // - Append Pithos Block on the existing object
            hadoopConnector.appendPithosBlock(pithosPath.getContainer(),
                    pithosPath.getObjectAbsolutePath(), pithosBlock);

        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        }

        // internalClose();

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
        byte[] blockData = PithosSerializer.serializeFile(backupFile);
        String blockHash = null;
        String container = pithosPath.getContainer();
        String hashAlgo = hadoopConnector
                .getPithosContainerHashAlgorithm(container);
        util.dbgPrint("nextBlockOutputStream", hashAlgo);
        try {
            blockHash = util.computeHash(blockData, hashAlgo);
            if (!hadoopConnector.pithosObjectBlockExists(container, blockHash)) {
                nextBlock = new PithosBlock(blockHash, bytesWrittenToBlock,
                        blockData);
                blocks.add(nextBlock);
                bytesWrittenToBlock = 0;
            }
        } catch (NoSuchAlgorithmException e) {
            throw new IOException(e);
        }
    }

    // /**
    // * Close and save all information carefully on internal close
    // *
    // * @throws IOException
    // */
    // private synchronized void internalClose() throws IOException {
    // INode inode = new INode(INode.FILE_TYPES[1],
    // blocks.toArray(new Block[blocks.size()]));
    // store.storeINode(path, inode);
    // }

    @Override
    public synchronized void close() throws IOException {
        util.dbgPrint("close");
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
}
