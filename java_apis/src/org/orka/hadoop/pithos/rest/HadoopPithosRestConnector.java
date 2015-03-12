package org.orka.hadoop.pithos.rest;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.grnet.client.PithosRESTAPI;
import org.orka.hadoop.commons.Configurator;
import org.orka.hadoop.commons.Settings;

/***
 * This class extends Pithos REST API that is implemented by grnet and supports
 * the implementation of particular methods for the interaction between hadoop
 * and Pithos Storage System.
 * 
 * {@link: 
 * https://www.synnefo.org/docs/synnefo/latest/object-api-guide.html#object
 * -level}
 * 
 * @author dkelaidonis
 * @version 0.1
 * @since March, 2015
 */

public class HadoopPithosRestConnector extends PithosRESTAPI {

	private static final long serialVersionUID = 1L;
	private static final String CONFIGURATION_FILE = "hadoopPithosConfiguration.json";
	private static final Settings hadoopConfiguration = Configurator
			.load(CONFIGURATION_FILE);

	public HadoopPithosRestConnector() {
		// - implement aPithos RESTAPI instance
		super(hadoopConfiguration.getPithosUser().get("url"),// pithos auth-url
				hadoopConfiguration.getPithosUser().get("token"),// user-token
				hadoopConfiguration.getPithosUser().get("username"));// username

	}

	/***
	 * Method to get the metadata that correspond to a Pithos object stored
	 * under specific container (default: "Pithos")
	 * 
	 * @param container
	 *            : default is "Pithos", objectName: the requested object
	 * @throws IOException
	 */
	public Map<String, List<String>> getPithosObjectMetadata(String container,
			String objectName) throws IOException {
		// - Request Parameters
		HashMap<String, String> parameters = new HashMap<String, String>();
		parameters.put("format", "json"); // set it json so as to get response
											// in json format
		// - Request Header
		HashMap<String, String> headers = new HashMap<String, String>();

		// - Read data object
		return retrieve_object_metadata(objectName, container, parameters,
				headers);
	}

	/***
	 * Method to get/downloads chunk of a requested object from Pithos
	 * 
	 * @param container
	 *            : default is "Pithos", objectName: the requested object
	 * @throws IOException
	 */
	public Object getPithosObject(String container, String objectName)
			throws IOException {
		// - Request Parameters
		HashMap<String, String> parameters = new HashMap<String, String>();
		parameters.put("format", "json"); // set it json so as to get response
											// in json format
		parameters.put("hashmap", "false"); // set it false so as to get the
											// actual object
		// - Request Header
		HashMap<String, String> headers = new HashMap<String, String>();
		headers.put("Range", "bytes=0-9");

		// - Read data object
		return read_object_data(objectName, container, parameters, headers);
	}

}
