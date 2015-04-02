package org.orka.hadoop.commons;

import java.util.HashMap;
import java.util.Map;

/**
 * @since March, 2015
 * @author Dimitris G. Kelaidonis  (kelaidonis@gmail.com)
 * @version 0.1
 */
public class Settings {

	private Map<String, String> hadoopGeneralConfiguration = new HashMap<String, String>();
	private Map<String, String> hadoopUser = new HashMap<String, String>();
	private Map<String, String> pithosUser = new HashMap<String, String>();
	
	/**
	 * General parameters
	 */
	public Map<String, String> getHadoopGeneralConfiguration() {
		return hadoopGeneralConfiguration;
	}
	
	
	/**
	 * Hadoop user (on hdfs) parameters
	 */
	public Map<String, String> getHadoopUser() {
		return hadoopUser;
	}

	/**
	 * Pithos user parameters - (based on Pithos REST API by Konstantinos Vogias)
	 */
	public Map<String, String> getPithosUser() {
		return pithosUser;
	}
	
}