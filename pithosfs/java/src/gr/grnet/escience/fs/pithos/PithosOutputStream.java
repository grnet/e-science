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
 * Wraps OutputStream for streaming data into Pithos.
 */
public class PithosOutputStream extends OutputStream {

    private static String ERR_STREAM_CLOSED = "Stream closed";

    /** Hadoop configuration. */
    private Configuration conf;

    private int bufferSize;

    /** Destination path. */
    private PithosPath pithosPath;

    /** pithos block size. */
    private long blockSize;

    /** temporary file buffer. */
    private File backupFile;

    /** stream connected to temporary file buffer. */
    private OutputStream backupStream;

    /** holds the state of the backupFile stream. */
    private boolean closed = false;
    
    /** static variable used by setter and getter that holds the state of the backupFile stream*/
    private static boolean streamStatus = false;

    /** current position. */
    private int pos = 0;

    /** file position. */
    private long filePos = 0;

    private int bytesWrittenToBlock = 0;

    private byte[] outBuf = null;

    /** holds reference to next block to stream to pithos. */
    private PithosBlock nextBlock = null;

    /** holds path to temporary folder used for file buffer. */
    private File tmpDir = null;

    private File tmpBackupFile = null;

    private int remaining = 0;

    private int toWrite = 0;

    private int workingPos = 0;

    private byte[] blockData = null;

    private String blockHash = null;

    /** pithos container. */
    private String container = null;

    /** The hash algorithm name. */
    private String hashAlgo = null;

    /**
     * Instantiates a new pithos output stream.
     *
     * @param conf
     *            HDFS configuration
     * @param path
     *            pithos file path
     * @param blocksize
     *            size of block
     * @param buffersize
     *            size of buffer
     * @throws IOException
     *             backupFile stream failed to open.
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
     * Creates a backup file for buffering before streaming to pithos.
     *
     * @return File
     * @throws IOException
     *             create file failed.
     */
    private File newBackupFile() throws IOException {
        tmpDir = new File(conf.get("hadoop.tmp.dir"));
        if (!tmpDir.exists() && !tmpDir.mkdirs()) {
            throw new IOException(
                    "Cannot create local pithos buffer directory: " + tmpDir);
        }
        tmpBackupFile = File.createTempFile("output-", ".tmp", tmpDir);
        tmpBackupFile.deleteOnExit();

        return tmpBackupFile;
    }

    public long getPos() throws IOException {
        return filePos;
    }

    /*
     * (non-Javadoc)
     * 
     * @see java.io.OutputStream#write(int)
     */
    @Override
    public synchronized void write(int b) throws IOException {

        if (closed) {
            throw new IOException(ERR_STREAM_CLOSED);
        }

        if ((bytesWrittenToBlock + pos == blockSize) || (pos >= bufferSize)) {
            flush();
        }
        outBuf[pos++] = (byte) b;
        filePos++;
    }

    /*
     * (non-Javadoc)
     * 
     * @see java.io.OutputStream#write(byte[], int, int)
     */
    @Override
    public synchronized void write(byte[] b, int off, int len)
            throws IOException {
        if (closed) {
            throw new IOException(ERR_STREAM_CLOSED);
        }
        while (len > 0) {

            remaining = bufferSize - pos;
            toWrite = Math.min(remaining, len);
            // Commented out for causing ArrayIndexOutOfBoundsException
            // when writing to Pithos.
            //outBuf[pos] = b[off];

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

    /*
     * (non-Javadoc)
     * 
     * @see java.io.OutputStream#flush()
     */
    @Override
    public synchronized void flush() throws IOException {

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
     * Flushes data to output buffer.
     *
     * @param maxPos
     *            position to which backup data
     * @throws IOException
     *             write to backupFile failed.
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
     * Streams block to pithos when file buffer full. Prepares next file buffer.
     *
     * @throws IOException
     *             backupFile not found.
     */
    private synchronized void endBlock() throws IOException {

        backupStream.close();

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
     * Creates output stream for next block of data.
     *
     * @throws IOException
     *             serialization or block hash calculation error.
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
                bytesWrittenToBlock = 0;
            }
        } catch (NoSuchAlgorithmException e) {
            throw new IOException(e);
        } catch (Exception e) {
            Utils.dbgPrint("nextBlockOutputStream exception >", e.toString());
            throw new IOException(e);
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see java.io.OutputStream#close()
     */
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
        setStreamStatus(closed);
    }

    /*
     * sets the stream status to get used by another class
     */
    public synchronized static void setStreamStatus(boolean closed) {
        streamStatus = closed;
    }
    
    /*
     * returns the stream status when asked from another class
     */
    public synchronized static boolean getStreamStatus() {
        return streamStatus;
    }

}
