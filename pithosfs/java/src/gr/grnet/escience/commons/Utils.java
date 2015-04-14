package gr.grnet.escience.commons;

import java.io.UnsupportedEncodingException;
import java.security.*;

public class Utils {
	
	
	/**
	 * Get the hash 
	 * container
	 * 
	 * @param byteData
	 *            : the byte array to get the digest of
	 * @param hash_algorithm
	 *            : the name of the hash algorithm to use
	 * @return bytestring hash representation of the input digest
	 */	
	public String computeHash(byte[] byteData, String hash_algorithm) throws NoSuchAlgorithmException, UnsupportedEncodingException{
		// eg. hash_algorithm = "SHA-256";
	    MessageDigest digest = MessageDigest.getInstance(hash_algorithm);
	    digest.reset();
	    
	    StringBuffer sb = new StringBuffer();
	    
	    for (int i = 0; i < byteData.length; i++){
	      sb.append(Integer.toString((byteData[i] & 0xff) + 0x100, 16).substring(1));
	    }
	    return sb.toString();
	}
	
	/**
	 * Get the hash 
	 * container
	 * 
	 * @param utf-8 string
	 *            : the string to get the digest of
	 * @param hash_algorithm
	 *            : the name of the hash algorithm to use
	 * @return bytestring hash representation of the input digest
	 */	
	public String computeHash(String input, String hash_algorithm) throws NoSuchAlgorithmException, UnsupportedEncodingException{
		// eg. hash_algorithm = "SHA-256";
	    MessageDigest digest = MessageDigest.getInstance(hash_algorithm);
	    digest.reset();

	    byte[] byteData = digest.digest(input.getBytes("UTF-8"));
	    StringBuffer sb = new StringBuffer();

	    for (int i = 0; i < byteData.length; i++){
	      sb.append(Integer.toString((byteData[i] & 0xff) + 0x100, 16).substring(1));
	    }
	    return sb.toString();
	}
	
	public Utils() {
	}
}
