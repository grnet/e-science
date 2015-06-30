package gr.grnet.escience.pithos.rest;

import java.util.HashMap;

/**
 * The Class PithosRequest.
 */
public class PithosRequest {

    HashMap<String, String> parameters = new HashMap<String, String>();
    
    HashMap<String, String> headers = new HashMap<String, String>();

    public HashMap<String, String> getRequestParameters() {
        return parameters;
    }

    public HashMap<String, String> getRequestHeaders() {
        return headers;
    }

}
