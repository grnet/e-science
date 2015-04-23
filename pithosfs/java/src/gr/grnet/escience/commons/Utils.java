package gr.grnet.escience.commons;

import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URLEncoder;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class Utils {

	private static final boolean DEBUG = false;
	
	public Utils() {
	}
	
	/**
	 * Get the hash container
	 * 
	 * @param byteData
	 *            : the byte array to get the digest of
	 * @param hashAlgorithm
	 *            : the name of the hash algorithm to use
	 * @return bytestring hash representation of the input digest
	 */
	public String computeHash(byte[] byteData, String hashAlgorithm)
			throws NoSuchAlgorithmException, UnsupportedEncodingException {
		/** eg. hash_algorithm = "SHA-256"; */
	    MessageDigest digest = MessageDigest.getInstance(hashAlgorithm);
	    digest.reset();
	    
        byte[] byteDatad = digest.digest(byteData);
	    StringBuilder sb = new StringBuilder();
	    
	    for (int i = 0; i < byteDatad.length; i++){
	      sb.append(Integer.toString((byteDatad[i] & 0xff) + 0x100, 16).substring(1));
	    }
	    return sb.toString();
	}

	/**
	 * Get the hash container
	 * 
	 * @param utf
	 *            -8 string : the string to get the digest of
	 * @param hashAlgorithm
	 *            : the name of the hash algorithm to use
	 * @return bytestring hash representation of the input digest
	 */
	public String computeHash(String input, String hashAlgorithm)
			throws NoSuchAlgorithmException, UnsupportedEncodingException {
		/** eg. hash_algorithm = "SHA-256"; */
		MessageDigest digest = MessageDigest.getInstance(hashAlgorithm);
		digest.reset();

	    byte[] byteData = digest.digest(input.getBytes("UTF-8"));
	    StringBuilder sb = new StringBuilder();

		for (int i = 0; i < byteData.length; i++) {
			sb.append(Integer.toString((byteData[i] & 0xff) + 0x100, 16)
					.substring(1));
		}
		return sb.toString();
	}

	/**
	 * Return an escaped url using form encoding and character replacement
	 * 
	 * @param url
	 * @return url escaped path
	 * @throws UnsupportedEncodingException
	 */
	public String urlEscape(String url) throws UnsupportedEncodingException {
		return URLEncoder.encode(url, "UTF-8")
				.replaceAll("\\+", "%20").replaceAll("\\%21", "!")
				.replaceAll("\\%27", "'").replaceAll("\\%28", "(")
				.replaceAll("\\%29", ")").replaceAll("\\%7E", "~");
	}

	/**
	 * Construct a URI from passed components and return the escaped and encoded
	 * url
	 * 
	 * @param scheme
	 *            : can be null for partial path
	 * @param host
	 *            : can be null for partial path
	 * @param path
	 * @param fragment
	 *            : can be null for partial path
	 * @return url escaped path
	 * @throws URISyntaxException
	 */
	public String urlEscape(String scheme, String host, String path,
			String fragment) throws URISyntaxException {
		URI uri = new URI(scheme, host, path, fragment);
		return uri.toASCIIString();
	}

	/**
	 * Thin wrapper around System.err.println for quick tracing
	 * 
	 * @param args
	 *            : variable length array of objects
	 */
	public void dbgPrint(Object... args) {
		if (!DEBUG){
			return;
			}
		String formatter = "DEBUG:";
		for (int i = 0; i < args.length; i++) {
			formatter+=" %s";
		}
		formatter+="\n";
		System.err.format(formatter, args);
	}
	
}
