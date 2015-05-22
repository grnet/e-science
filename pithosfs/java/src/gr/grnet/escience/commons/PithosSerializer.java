package gr.grnet.escience.commons;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.StringWriter;

public class PithosSerializer {

	private static StringWriter sWriter;
	private static PrintWriter pWriter;

	public PithosSerializer() {
	}

	/**
	 * This method convert an exception from any type of instance into a string
	 * 
	 * @param exeptiton
	 *            :the instance of the exception
	 * @return a given exception as String
	 */
	public static String exceptionToStrign(Exception exeptiton) {
		// - Create String writer instance
		sWriter = new StringWriter();
		// - Create printwriter instance and assign a String writer instance
		pWriter = new PrintWriter(sWriter);
		// - Add exception content into the printwriter instance
		exeptiton.printStackTrace(pWriter);

		// - return the exception message as string
		return sWriter.toString();
	}

	// convert InputStream to String
	/**
	 * 
	 * @param is
	 *            : the input stream
	 * @return the inputstrem as string
	 */
	public static String inputStreamToString(InputStream is) {

		BufferedReader br = null;
		StringBuilder sb = new StringBuilder();

		String line;
		try {

			br = new BufferedReader(new InputStreamReader(is));
			while ((line = br.readLine()) != null) {
				sb.append(line);
			}

		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}

		return sb.toString();

	}

	/**
	 * Serialize a file into bytes array
	 * 
	 * @param inputFile
	 *            : tha file that should be serialized into bytes array
	 * @return a File as bytes []
	 */
	public static byte[] serializeFile(File inputFile) {
		// -Crete file input stream
		FileInputStream fileInputStream = null;

		// - Convert File in bytes []
		byte[] block_data_bytes = new byte[(int) inputFile.length()];

		// - Perform the conversion
		try {
			// - Convert file into array of bytes
			fileInputStream = new FileInputStream(inputFile);
			fileInputStream.read(block_data_bytes);
			fileInputStream.close();

			// - return the bytes array
			return block_data_bytes;
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}

	/**
	 * Deserialize a byte array into File
	 * 
	 * @param data
	 *            the byte array that should be desirialized int File
	 * @return return a File that actually constitutes the bytes that were
	 *         deserialized
	 */
	public static File deserializeFile(byte[] data) {
		// convert array of bytes into file
		FileOutputStream fileOuputStream;
		try {
			// - Create file
			File block = new File("block");
			// - Create output stream with data to the file
			fileOuputStream = new FileOutputStream(block);
			fileOuputStream.write(data);
			fileOuputStream.close();
			// - return the file
			return block;
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
	}

}
