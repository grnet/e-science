package gr.grnet.escience.pithos.rest;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.Gson;

public class PithosResponse {

	Map<String, List<String>> pithosResponse = new HashMap<String, List<String>>();

	/**
	 * @return the response object from Pithos
	 */
	public Map<String, List<String>> getResponseData() {
		return pithosResponse;
	}

	/**
	 * Set the response structure based on the identified structure in the
	 * coressponding Pithos API
	 * 
	 * @param _response
	 *            : structured data based on the structure of the Pithos
	 *            response
	 */
	public void setResponseData(Map<String, List<String>> _response) {
		this.pithosResponse = _response;
	}
	
	
	@Override
	public String toString() {
		// TODO Auto-generated method stub
		return (new Gson()).toJson(this);
	}
}
