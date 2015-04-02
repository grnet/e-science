package org.orka.hadoop.pithos.rest;

import java.util.HashMap;

class PithosRequest {

	HashMap<String, String> parameters = new HashMap<String, String>();
	HashMap<String, String> headers = new HashMap<String, String>();

	/**
	 * @return the parameters for the pithos request
	 */
	public HashMap<String, String> getRequestParameters() {
		return parameters;
	}

	/**
	 * @return the arguments for the Pithos request Headers
	 */
	public HashMap<String, String> getRequestHeaders() {
		return headers;
	}

}
