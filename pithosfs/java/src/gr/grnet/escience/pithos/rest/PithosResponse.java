package gr.grnet.escience.pithos.rest;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.Gson;

public class PithosResponse {

    Map<String, List<String>> pithosResp = new HashMap<String, List<String>>();

    /**
     * @return the response object from Pithos
     */
    public Map<String, List<String>> getResponseData() {
        return pithosResp;
    }

    /**
     * Set the response structure based on the identified structure in the
     * corresponding Pithos API
     * 
     * @param response
     *            : structured data based on the structure of the Pithos
     *            response
     */
    public void setResponseData(Map<String, List<String>> response) {
        this.pithosResp = response;
    }

    @Override
    public String toString() {
        return (new Gson()).toJson(this);
    }
}
