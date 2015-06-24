package gr.grnet.escience.fs.pithos;

import gr.grnet.escience.commons.PithosSerializer;
import gr.grnet.escience.commons.Utils;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.security.NoSuchAlgorithmException;

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
     * flag if stream closed
     */
    private static boolean closed;

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
    private byte[] outBuf = null;

    /**
     * current block to store to pithos
     */
    private PithosBlock nextBlock = null;

    private File dir = null;
    private File result = null;
    private int remaining = 0;
    private int toWrite = 0;
    private int workingPos = 0;
    private byte[] blockData = null;
    private String blockHash = null;
    private String container = null;
    private String hashAlgo = null;

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

        this.conf = conf;
        this.pithosPath = path;
        this.blockSize = blocksize;
        this.backupFile = newBackupFile();
        this.backupStream = new FileOutputStream(backupFile);
        this.bufferSize = buffersize;
        this.outBuf = new byte[buffersize];
    }

    /**
     * method for creating backup file for buffering before streaming to pithos
     * 
     * @return File
     * @throws IOException
     */
    private File newBackupFile() throws IOException {
        dir = new File(conf.get("hadoop.tmp.dir"));
        if (!dir.exists() && !dir.mkdirs()) {
            throw new IOException(
                    "Cannot create local pithos buffer directory: " + dir);
        }
        result = File.createTempFile("output-", ".tmp", dir);
        result.deleteOnExit();

        return result;
    }

    public long getPos() throws IOException {
        return filePos;
    }

    @Override
    public synchronized void write(int b) throws IOException {

        if (isClosed()) {
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
        if (isClosed()) {
            throw new IOException(ERR_STREAM_CLOSED);
        }
        while (len > 0) {

            remaining = bufferSize - pos;
            toWrite = Math.min(remaining, len);

            outBuf[pos] = b[off];

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

        if (isClosed()) {
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
        workingPos = Math.min(pos, maxPos);

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
        Utils.dbgPrint("endBlock");
        //
        // Done with local copy
        //
        backupStream.close();

        //
        // - Load file bytes
        nextBlockOutputStream();

        // - Append Pithos Block on the existing object
        PithosFileSystem.getHadoopPithosConnector().appendPithosBlock(
                pithosPath.getContainer(), pithosPath.getObjectAbsolutePath(),
                nextBlock);

        //
        // Delete local backup, start new one
        //
        backupFile.delete();
        backupFile = null;
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
        blockData = PithosSerializer.serializeFile(backupFile);
        container = pithosPath.getContainer();
        hashAlgo = PithosFileSystem.getHadoopPithosConnector()
                .getPithosContainerHashAlgorithm(container);

        try {
            blockHash = Utils.computeHash(blockData, hashAlgo);
            if (!PithosFileSystem.getHadoopPithosConnector()
                    .pithosObjectBlockExists(container, blockHash)) {
                nextBlock = new PithosBlock(blockHash, bytesWrittenToBlock,
                        blockData);
                // blocks.add(nextBlock);
                bytesWrittenToBlock = 0;
            }
        } catch (NoSuchAlgorithmException e) {
            throw new IOException(e);
        } catch (Exception e) {
            Utils.dbgPrint("nextBlockOutputStream exception >", e.toString());
            throw new IOException(e);
        }
    }

    @Override
    public synchronized void close() throws IOException {

        if (isClosed()) {
            return;
        }

        flush();
        if (filePos == 0 || bytesWrittenToBlock != 0) {
            endBlock();
        }

        backupStream.close();
        backupFile.delete();

        super.close();
        setClosed(true);
    }

    public static boolean isClosed() {
        return closed;
    }

    public static void setClosed(boolean flag) {
        closed = flag;
    }

}
