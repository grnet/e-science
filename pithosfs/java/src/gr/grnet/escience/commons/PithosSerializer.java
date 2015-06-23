package gr.grnet.escience.commons;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Base64;

public class PithosSerializer {

    private static FileInputStream fileInputStream = null;
    private static ByteArrayOutputStream baos = null;
    private static byte[] buffer = null;
    private static byte[] blockDataBytes = null;
    private static int bytesRead = 0;

    private PithosSerializer() {
    }

    /**
     * 
     * @param is
     *            : the input stream
     * @return the inputstream as Base64 encoded string
     */
    public static String inputStreamToString(InputStream is) throws IOException {

        try {
            baos = new ByteArrayOutputStream();
            buffer = new byte[1024];
            int length = 0;
            while ((length = is.read(buffer)) != -1) {
                baos.write(buffer, 0, length);
            }
        } catch (IOException e) {
            Utils.dbgPrint("PithosSerializer#inputStreamToString error >",e.getMessage());
            throw new IOException(e);
        } 
        return Base64.getEncoder().encodeToString(baos.toByteArray());
    }

    /**
     * Serialize a file into bytes array
     * 
     * @param inputFile
     *            : the file that should be serialized into bytes array
     * @return a File as bytes []
     */
    public static byte[] serializeFile(File inputFile) throws IOException {
        // -Create file input stream
        fileInputStream = null;

        // - Convert File in bytes []
        blockDataBytes = new byte[(int) inputFile.length()];
        bytesRead = 0;

        Utils.dbgPrint("serializeFile inputFile.length >", inputFile.length());

        // - Perform the conversion
        try {
            // - Convert file into array of bytes
            fileInputStream = new FileInputStream(inputFile);
            bytesRead = fileInputStream.read(blockDataBytes);
            Utils.dbgPrint("serializeFile fileInputStream read > ", bytesRead);
            Utils.dbgPrint("serializeFile blockDataBytes > ",
                    blockDataBytes.length);

            // - return the bytes array
            return blockDataBytes;
        } finally {
            if (fileInputStream != null) {
                fileInputStream.close();
            }
        }
    }

    /**
     * Deserialize a byte array into File
     * 
     * @param data
     *            the byte array that should be deserialized int File
     * @return return a File that actually constitutes the bytes that were
     *         deserialized
     */
    public static File deserializeFile(byte[] data) throws IOException {
        // convert array of bytes into file
        FileOutputStream fileOutputStream = null;
        try {
            // - Create file
            File block = new File("block");
            // - Create output stream with data to the file
            fileOutputStream = new FileOutputStream(block);
            fileOutputStream.write(data);

            // - return the file
            return block;
        } finally {
            if (fileOutputStream != null) {
                fileOutputStream.close();
            }
        }
    }
}
