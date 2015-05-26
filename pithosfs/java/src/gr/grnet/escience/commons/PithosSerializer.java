package gr.grnet.escience.commons;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

public class PithosSerializer {

    private static BufferedReader br = null;
    private static StringBuilder sb = null;
    private static String line = null;
    private static FileInputStream fileInputStream = null;
    private static byte[] blockDataBytes = null;
    private static int bytesRead = 0;
    private static InputStreamReader inputStreamReader = null;

    private PithosSerializer() {
    }

    /**
     * 
     * @param is
     *            : the input stream
     * @return the inputstream as string
     */
    public static String inputStreamToString(InputStream is) throws IOException {

        try {
            sb = new StringBuilder();
            inputStreamReader = new InputStreamReader(is);
            br = new BufferedReader(inputStreamReader);

            while ((line = br.readLine()) != null) {
                sb.append(line);
            }

        } finally {
            if (br != null) {
                br.close();
            }
            if (inputStreamReader != null) {
                inputStreamReader.close();
            }
        }

        return sb.toString();

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
