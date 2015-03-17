package org.grnet.client;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.Serializable;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.URL;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

/**
 * @author kostas vogias
 * @version v1.0
 * 
 */
public class PithosRESTAPI implements Serializable {

	private static final long serialVersionUID = 7607132138602167015L;
	private static final String VERSION = "v1.0";

	private String url = "";
	private String X_Auth_Token = "";
	private HttpURLConnection con = null;
	private String username = "";

	public PithosRESTAPI(String url, String X_Auth_Token, String username) {
		this.url = url;
		this.X_Auth_Token = X_Auth_Token;
		this.username = username;
	}

	/**
	 * 
	 * @return The PithosClient version in String
	 */
	public static String getVersion() {
		return VERSION;
	}

	private void setConnection(HttpURLConnection con) {
		this.con = con;
	}

	public String getX_Auth_Token() {
		return X_Auth_Token;
	}

	public void setX_Auth_Token(String x_Auth_Token) {
		X_Auth_Token = x_Auth_Token;
	}

	public String getUsername() {
		return username;
	}

	public void setUsername(String username) {
		this.username = username;
	}

	/**
	 * 
	 * @return The URL of the Pithos instance.
	 */
	public String getUrl() {
		return url;
	}

	/**
	 * 
	 * @return The HttpURLConnection for Pithos communication
	 */
	private HttpURLConnection getConnection() {
		return con;
	}

	/**
	 * Creates,forms a URL object and finally opens a HttpURLConnection.
	 * 
	 * @param url
	 *            The URL to Pithos instance.
	 * @param properties
	 *            The various URL properties.
	 */
	private void setUrl(String url, HashMap<String, String> properties) {

		if (!properties.isEmpty()) {
			Iterator<String> keys = properties.keySet().iterator();

			while (keys.hasNext()) {
				String key = keys.next();
				String value = properties.get(key);

				url = add_parameter(url, key, value);

			}
		}

		try {
			URL url2 = new URL(url);

			this.setConnection((HttpURLConnection) url2.openConnection());

		} catch (MalformedURLException e) {
			// TODO Auto-generated catch block
			System.err.println("Error-->Malformed URL...");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			System.err.println("Error-->Invalid Input for connection...");
		}
	}

	/**
	 * Checks whether the Authentication Token is given.
	 * 
	 * @return True or false
	 */
	private boolean checkConf() {

		if (getX_Auth_Token() == null)
			return false;
		else
			return true;
	}

	/**
	 * Internal helping method for URL forming.
	 * 
	 * @param url
	 * @param name
	 * @param value
	 * @return String reperesentation of the input URL
	 */
	private String add_parameter(String url, String name, String value) {
		if (!url.contains("?"))
			url += "?" + name + "=" + value;
		else
			url += "&" + name + "=" + value;

		return url;

	}

	/**
	 * Adds the various user defined headers to the HttpURLConnection object.
	 * 
	 * @param headers
	 * @param method
	 * @throws ProtocolException
	 */
	private void setHeaders(HashMap<String, String> headers, String method)
			throws ProtocolException {

		this.getConnection().setRequestProperty("X-Auth-Token",
				getX_Auth_Token());
		Iterator<String> iterator = headers.keySet().iterator();

		while (iterator.hasNext()) {
			String headerName = iterator.next();

			String headerValue = headers.get(headerName);

			this.getConnection().setRequestProperty(headerName, headerValue);

		}

		this.getConnection().setRequestMethod(method);

	}

	/**
	 * Main method for creating and forming an HttpURLConnection.
	 * 
	 * @param url
	 * @param method
	 * @param properties
	 * @param headers
	 * @throws ProtocolException
	 */
	private void configureConnection(String url, String method,
			HashMap<String, String> properties, HashMap<String, String> headers)
			throws ProtocolException {
		//
		// if (this.getConnection() != null) {
		// System.out.println("Closing connection");
		// this.getConnection().disconnect();
		//
		// }

		setUrl(url, properties);
		setHeaders(headers, method);

	}

	// ------------Top level operations---------------------
	/**
	 * Sends a request to list other accounts that share objects to the user.
	 * 
	 * @param parameters
	 *            The request parameters.
	 * @param headers
	 *            The request headers.
	 * @my.headers <pre>
	 * 1.<strong>limit(optional)</strong> (The amount of results requested (default is 10000)).
	 * 2.<strong>marker(optional)</strong> (Return containers with name lexicographically after marker).
	 * 3.<strong>format(optional)</strong> (Optional extended reply type (can be json or xml)).
	 * </pre>
	 * @my.attributes <strong>X-Auth-Token(mandatory)</strong> (The user token).
	 * @return <p>
	 *         A list of account names. If a format=xml or format=json argument
	 *         is given, extended information on the accounts will be returned,
	 *         serialized in the chosen format. For each account, the
	 *         information will include the following (names will be in lower
	 *         case and with hyphens replaced with underscores).
	 *         </p>
	 * @return.code 200(OK)-The request succeeded
	 * @return.code 204 (No content)-The user has no access to other accounts
	 *              (only for non-extended replies)
	 * 
	 */
	public String list_sharing_accounts(HashMap<String, String> parameters,
			HashMap<String, String> headers) throws IOException {

		if (checkConf()) {
			configureConnection(getUrl(), "GET", parameters, headers);
			System.out.println("Listing sharing accounts for user with token:"
					+ getX_Auth_Token());
			System.out.println("Sending 'GET' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();

			if (responseCode == 200) {
				BufferedReader in = new BufferedReader(new InputStreamReader(
						this.getConnection().getInputStream()));

				String inputLine;
				StringBuffer response = new StringBuffer();

				while ((inputLine = in.readLine()) != null) {
					response.append(inputLine);
				}
				in.close();
				System.out.println(getConnection().getHeaderFields());
				return response.toString();

			} else {
				System.out.println(getConnection().getHeaderFields());
				return String.valueOf(responseCode);

			}
		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	// ----------Account level operations-----------------
	/**
	 * Retrieve account related information
	 * 
	 * @param parameters
	 *            The request parameters.
	 * @param headers
	 *            The request headers.
	 * @my.headers 1.<strong>until(optional)</strong> (Timestamp).
	 * @my.attributes <pre>
	 * 1.<strong>X-Auth-Token(mandatory).</strong>The user token.
	 * 2.<strong>If-Modified-Since (optional).</strong>Retrieve if account has changed since provided timestamp.
	 * 3.<strong>If-Unmodified-Since(optional.)</strong>Retrieve if account has not changed since provided timestamp.
	 * </pre>
	 * @return The account information contained in response header.
	 * @throws IOException
	 */
	public Map<String, List<String>> account_info(
			HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {

			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}

			String urlCloned = getUrl() + "/" + getUsername();
			configureConnection(urlCloned, "HEAD", parameters, headers);
			System.out
					.println("Retrieving account metadata for user with token:"
							+ getX_Auth_Token());
			System.out.println("Sending 'HEAD' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();

			if (responseCode == 204) {

				return getConnection().getHeaderFields();

			} else {
				System.err.println(String.valueOf(responseCode));

				return getConnection().getHeaderFields();
			}

		} else {
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * List account containers
	 * 
	 * @param parameters
	 *            The request parameters.
	 * @param headers
	 *            The request headers.
	 * @my.attributes <pre>
	 * 1.<strong>until(optional)</strong> (Timestamp).
	 * </pre>
	 * @my.headers <pre>
	 * 1.<strong>X-Auth-Token(mandatory).</strong>The user token.
	 * 2.<strong>If-Modified-Since (optional).</strong>Retrieve if account has changed since provided timestamp.
	 * 3.<strong>If-Unmodified-Since(optional.)</strong>Retrieve if account has not changed since provided timestamp.
	 * </pre>
	 * @return <p>
	 *         A string containing a list of container names with a specified
	 *         format.
	 *         </p>
	 * @throws IOException
	 */
	public String list_account_containers(HashMap<String, String> parameters,
			HashMap<String, String> headers) throws IOException {

		if (checkConf()) {
			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}
			String urlCloned = getUrl() + "/" + getUsername();
			configureConnection(urlCloned, "GET", parameters, headers);
			System.out
					.println("Listing containers for the account of user with token:"
							+ getX_Auth_Token());
			System.out.println("Sending 'GET' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();

			if (responseCode == 200) {
				BufferedReader in = new BufferedReader(new InputStreamReader(
						this.getConnection().getInputStream()));

				String inputLine;
				StringBuffer response = new StringBuffer();

				while ((inputLine = in.readLine()) != null) {
					response.append(inputLine);
				}
				in.close();
				System.out.println(getConnection().getHeaderFields());
				return response.toString();

			} else {
				System.out.println(getConnection().getHeaderFields());
				return String.valueOf(responseCode);

			}

		} else {
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * Update account metadata.
	 * 
	 * @param parameters
	 *            The request parameters.
	 * @param headers
	 *            The request headers.
	 * @my.headers <pre>
	 * 1.<strong>X-Account-Group-*</strong>.Optional user defined groups.
	 * 2.<strong>X-Account-Meta-*</strong>.Optional user defined metadata.
	 * </pre>
	 * @my.attributes 1.<strong>update</strong>.Do not replace metadata/groups
	 *                (no value parameter)
	 * @return No reply content/headers,only response code.
	 * @return.code <pre>
	 * 202-Accepted
	 * 400-The metadata exceed in number the allowed account metadata or the groups exceed in number the allowed groups
	 *     or the group members exceed in number the allowed group members
	 * </pre>
	 * @throws IOException
	 */
	public String update_account_metadata(HashMap<String, String> parameters,
			HashMap<String, String> headers) throws IOException {

		if (checkConf()) {
			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}
			String urlCloned = getUrl() + "/" + getUsername();
			parameters.put("update", "True");
			configureConnection(urlCloned, "POST", parameters, headers);
			System.out
					.println("Updating account metadata for the account of user with token:"
							+ getX_Auth_Token());
			System.out.println("Sending 'POST' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();

			System.out.println(getConnection().getHeaderFields());
			return String.valueOf(responseCode);

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	// ----------Container level operations-----------------

	/**
	 * Retrieve container metadata.
	 * 
	 * @param container
	 *            The container of the object(default is pithos called
	 *            container).
	 * @param parameters
	 *            The request parameters.
	 * @param headers
	 *            The request headers.
	 * @my.headers <pre>
	 * 1.<strong>If-Modified-Since</strong>.Retrieve if container has changed since provided timestamp
	 * 2.<strong>If-Unmodified-Since</strong>.Retrieve if container has not changed since provided timestamp
	 * </pre>
	 * @my.attributes <pre>
	 * 1.<strong>until</strong>.Optional timestamp.
	 * </pre>
	 * @reply.headers <pre>
	 * 1.<strong>X-Container-Object-Count</strong>.The total number of objects in the container
	 * 2.<strong>X-Container-Bytes-Used</strong>.The total number of bytes of all objects stored
	 * 3.<strong>X-Container-Block-Size</strong>.The block size used by the storage backend
	 * 4.<strong>X-Container-Block-Hash</strong>.The hash algorithm used for block identifiers in object hashmaps
	 * 5.<strong>X-Container-Until-Timestamp</strong>.The last container modification date until the timestamp provided
	 * 6.<strong>X-Container-Object-Meta</strong>.A list with all meta keys used by objects (TBD)
	 * 7.<strong>X-Container-Policy-*</strong>.Container behavior and limits
	 * 8.<strong>X-Container-Meta-*</strong>.Optional user defined metadata
	 * 9.<strong>Last-Modified</strong>.The last container modification date (regardless of until)
	 * </pre>
	 * @return.code 204(No content) - The request succeeded.
	 * @return The reply headers
	 * @throws IOException
	 */
	public Map<String, List<String>> retrieve_container_info(String container,
			HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {
			if (container.equals("") || container == null)
				container = "pithos";

			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}
			String urlCloned = getUrl() + "/" + getUsername() + "/" + container;
			configureConnection(urlCloned, "HEAD", parameters, headers);
			System.out
					.println("Retrieving container metadata for the container:"
							+ container + " of user with token:"
							+ getX_Auth_Token());
			System.out.println("Sending 'HEAD' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();

			if (responseCode == 204) {

				return getConnection().getHeaderFields();

			} else {

				System.err.println(String.valueOf(responseCode));
				return getConnection().getHeaderFields();
			}

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * List container objects.
	 * 
	 * @param container
	 *            The container of the object(default is pithos called
	 *            container).
	 * @param parameters
	 *            The request parameters.
	 * @param headers
	 *            The request headers.
	 * @my.headers <pre>
	 * 1.<strong>If-Modified-Since</strong>.Retrieve if container has changed since provided timestamp
	 * 2.<strong>If-Unmodified-Since</strong>.Retrieve if container has not changed since provided timestamp
	 * </pre>
	 * @my.attributes <pre>
	 * 1.<strong>limit</strong>.The amount of results requested (default is 10000)
	 * 2.<strong>marker</strong>.Return containers with name lexicographically after marker
	 * 3.<strong>prefix</strong>.Return objects starting with prefix
	 * 4.<strong>delimiter</strong>.Return objects up to the delimiter (discussion follows)
	 * 5.<strong>path</strong>.Assume prefix=path and delimiter=/
	 * 6.<strong>format</strong>.Optional extended reply type (can be json or xml)
	 * 7.<strong>meta</strong>.Return objects that satisfy the key queries in the specified comma separated list (use <key>, !<key> for existence queries, <key><op><value> for value queries, where <op> can be one of =, !=, <=, >=, <, >)
	 * 8.<strong>shared</strong>.Show only objects (no value parameter)
	 * 9.<strong>public</strong>.Show only public objects (no value parameter / avalaible only for owner requests)
	 * 10.<strong>until</strong>.Optional timestamp.
	 * </pre>
	 * @reply.headers <pre>
	 * 1.<strong>X-Container-Block-Size</strong>.The block size used by the storage backend
	 * 2.<strong>X-Container-Block-Hash</strong>.The hash algorithm used for block identifiers in object hashmaps
	 * 3.<strong>Last-Modified</strong>.The last container modification date
	 * 4.<strong>X-Container-Object-Meta</strong>.A list with all meta keys used by allowed objects (TBD)
	 * </pre>
	 *                <p>
	 *                If a format=xml or format=json argument is given,extended
	 *                information on the objects will be returned, serialized in
	 *                the chosen format. For each object, the information will
	 *                include all object metadata, except user-defined (names
	 *                will be in lower case and with hyphens replaced with
	 *                underscores). User-defined metadata includes
	 *                X-Object-Meta-*, X-Object-Manifest, Content-Disposition
	 *                and Content-Encoding keys. Also, sharing directives will
	 *                only be included with the actual shared objects (inherited
	 *                permissions are not calculated):
	 *                </p>
	 * 
	 *                <pre>
	 * 1.<strong>name</strong>.The name of the object
	 * 2.<strong>hash</strong>.The ETag of the object
	 * 3.<strong>bytes</strong>.The size of the object
	 * 4.<strong>content_type</strong>.The MIME content type of the object
	 * 5.<strong>last_modified</strong>.The last object modification date (regardless of version)
	 * 6.<strong>x_object_hash</strong>.The Merkle hash
	 * 7.<strong>x_object_uuid</strong>.The object’s UUID
	 * 8.<strong>x_object_version</strong>.The object’s version identifier
	 * 9.<strong>x_object_version_timestamp</strong>.The object’s version timestamp
	 * 10.<strong>x_object_modified_by</strong>.The user that committed the object’s version
	 * 11.<strong>x_object_sharing</strong>.Object permissions (optional)
	 * 12.<strong>Object permissions (optional)</strong>.Allowed actions on object (optional)
	 * 13.<strong>x_object_public</strong>.Object’s publicly accessible URI (optional: present if the object is public and the request user is the object owner)
	 * </pre>
	 * @return.code <pre>
	 * 200(OK) - The request succeeded.
	 * 204(No Content) - The container has no objects (only for non-extended replies)
	 * 304(Not Modified) - The container has not been modified
	 * 403(Forbidden) - Public is requested but the request user is not the path owner
	 * 412(Precondition Failed) - The condition set can not be satisfied
	 * </pre>
	 * @return The response code.
	 * @throws IOException
	 */
	public String list_container_objects(String container,
			HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {
			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}
			String urlCloned = getUrl() + "/" + getUsername() + "/" + container;
			configureConnection(urlCloned, "GET", parameters, headers);
			System.out
					.println("Listing objects for the container:" + container
							+ " of the account of user with token:"
							+ getX_Auth_Token());
			System.out.println("Sending 'GET' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();

			if (responseCode == 200) {
				BufferedReader in = new BufferedReader(new InputStreamReader(
						this.getConnection().getInputStream()));

				String inputLine;
				StringBuffer response = new StringBuffer();

				while ((inputLine = in.readLine()) != null) {
					response.append(inputLine);
				}
				in.close();
				System.out.println(getConnection().getHeaderFields());
				return response.toString();

			} else {
				System.out.println(getConnection().getHeaderFields());
				return String.valueOf(responseCode);

			}

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * Create/update container.
	 * 
	 * @param container
	 *            The container of the object(default is pithos called
	 *            container).
	 * @param parameters
	 *            The request parameters.
	 * @param headers
	 *            The request headers.
	 * @my.headers <pre>
	 * 1.<strong>X-Container-Policy-*</strong>.Container behavior and limits
	 * 2.<strong>X-Container-Meta-*</strong>.Optional user defined metadata
	 * </pre>
	 * @return Reponse code
	 * @throws IOException
	 * @return.code <pre>
	 * 201 (Created) - The container has been created
	 * 202 (Accepted) - The request has been accepted
	 * 413 (Request Entity Too Large) - Insufficient quota to complete the request
	 * </pre>
	 */
	public String create_update_container(String container,
			HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {
			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}
			String urlCloned = getUrl() + "/" + getUsername() + "/" + container;
			configureConnection(urlCloned, "PUT", parameters, headers);
			System.out
					.println("Creating/Updating the container:" + container
							+ " of the account of user with token:"
							+ getX_Auth_Token());
			System.out.println("Sending 'PUT' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();
			System.out.println(getConnection().getHeaderFields());
			return String.valueOf(responseCode);

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * Update container metadata.
	 * 
	 * @param container
	 *            The container of the object(default is pithos called
	 *            container).
	 * @param parameters
	 *            The request parameters.
	 * @param headers
	 *            The request headers.
	 * @my.headers <pre>
	 * 1.<strong>Content-Length</strong>.The size of the supplied data (optional, to upload)
	 * 2.<strong>Content-Type</strong>.The MIME content type of the supplied data (optional, to upload)
	 * 3.<strong>Transfer-Encoding</strong>.Set to chunked to specify incremental uploading (if used, Content-Length is ignored)
	 * 4.<strong>X-Container-Policy-*</strong>.Container behavior and limits
	 * 5.<strong>X-Container-Meta-*</strong>.Optional user defined metadata
	 * </pre>
	 * @my.attributes <pre>
	 * 1.<strong>format</strong>.Optional hash list reply type (can be json or xml)
	 * 2.<strong>update</strong>.Do not replace metadata/policy (no value parameter)
	 * </pre>
	 * @return The response code
	 * @throws IOException
	 * @return.code <pre>
	 * 202 (Accepted) - The request has been accepted
	 * 400 (Bad Request) - The metadata exceed in number the allowed container metadata
	 * 413 (Request Entity Too Large) - Insufficient quota to complete the request
	 * </pre>
	 */

	public String update_container_metadata(String container,
			HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {
			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}
			String urlCloned = getUrl() + "/" + getUsername() + "/" + container;
			configureConnection(urlCloned, "POST", parameters, headers);
			System.out.println("Updating metadata of the container:"
					+ container + " of the account of user with token:"
					+ getX_Auth_Token());
			System.out.println("Sending 'POST' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();
			System.out.println(getConnection().getHeaderFields());
			return String.valueOf(responseCode);

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * Delete a specific container.
	 * 
	 * @param container
	 *            The container of the object(default is pithos called
	 *            container).
	 * @param parameters
	 *            The request parameters.
	 * @param headers
	 *            The request headers.
	 * @my.headers <pre>
	 * 1.<strong>until</strong>.Optional timestamp
	 * 2.<strong>delimiter</strong>.Optional delete objects starting with container name and delimiter
	 * </pre>
	 * @return Response code
	 * @throws IOException
	 * @return.code <pre>
	 * 204 (No Content) - The request succeeded
	 * 409 (Conflict) - The container is not empty
	 * </pre>
	 */
	public String delete_container(String container,
			HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {
			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}
			String urlCloned = getUrl() + "/" + getUsername() + "/" + container;
			configureConnection(urlCloned, "DELETE", parameters, headers);
			System.out
					.println("Deleting the container:" + container
							+ " of the account of user with token:"
							+ getX_Auth_Token());
			System.out.println("Sending 'DELETE' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();
			System.out.println(getConnection().getHeaderFields());
			return String.valueOf(responseCode);

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	// ----------Item level operations-----------------
	/**
	 * Retrieve object metadata.
	 * 
	 * @param filename
	 *            The object name representation.
	 * @param container
	 *            The container of the object(default is pithos called
	 *            container).
	 * @param parameters
	 *            The request parameters.
	 * @param headers
	 *            The request headers.
	 * @my.headers <pre>
	 * 1.<strong>If-Match</strong>.Retrieve if ETags match
	 * 2.<strong>If-None-Match</strong>.Retrieve if ETags don’t match
	 * 3.<strong>If-Modified-Since</strong>.Retrieve if object has changed since provided timestamp
	 * 4.<strong>If-Unmodified-Since</strong>.Retrieve if object has not changed since provided timestamp
	 * </pre>
	 * @my.attributes <strong>version</strong>.Optional version identifier
	 * @reply.headers <pre>
	 * 1.<strong>ETag</strong>.The ETag of the object
	 * 2.<strong>Content-Length</strong>.The size of the object
	 * 3.<strong>Content-Type</strong>.The MIME content type of the object
	 * 4.<strong>Last-Modified</strong>.The last object modification date (regardless of version)
	 * 5.<strong>Content-Encoding</strong>.The encoding of the object (optional)
	 * 6.<strong>Content-Disposition</strong>.The presentation style of the object (optional)
	 * 7.<strong>X-Object-Hash</strong>.The Merkle hash
	 * 8.<strong>X-Object-UUID</strong>.The object’s UUID
	 * 9.<strong>X-Object-Version</strong>.The object’s version identifier
	 * 10.<strong>X-Object-Version-Timestamp</strong>.The object’s version timestamp
	 * 11.<strong>X-Object-Modified-By</strong>.The user that committed the object’s version
	 * 12.<strong>X-Object-Manifest</strong>.Object parts prefix in <container>/<object> form (optional)
	 * 13.<strong>X-Object-Sharing</strong>.Object permissions (optional)
	 * 14.<strong>X-Object-Shared-By</strong>.Object inheriting permissions (optional)
	 * 15.<strong>X-Object-Allowed-To</strong>.Allowed actions on object (optional)
	 * 16.<strong>X-Object-Public</strong>.Object’s publicly accessible URI (optional: present if the object is public and the request user is the object owner)
	 * 17.<strong>X-Object-Meta-*</strong>.Optional user defined metadata
	 * </pre>
	 * @return The response headers
	 * @throws IOException
	 * @return.code 200(No Content)-The request succeeded.
	 */
	public Map<String, List<String>> retrieve_object_metadata(String filename,
			String container, HashMap<String, String> parameters,
			HashMap<String, String> headers) throws IOException {

		if (checkConf()) {
			if (container.equals("") || container == null)
				container = "pithos";

			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}
			String urlCloned = getUrl() + "/" + getUsername() + "/" + container
					+ "/" + filename;
			configureConnection(urlCloned, "HEAD", parameters, headers);
			System.out.println("Retrieving the metadata for the item:"
					+ filename + " of user with token:" + getX_Auth_Token());
			System.out.println("Sending 'HEAD' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();

			if (responseCode == 200) {

				return getConnection().getHeaderFields();

			} else {

				System.err.println(String.valueOf(responseCode));
				return getConnection().getHeaderFields();
			}

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * Either downloads an object or shows object info(JSON,XML).
	 * 
	 * @param filename
	 *            The object name representation.
	 * @param container
	 *            The container of the object(default is pithos called
	 *            container).
	 * @param parameters
	 *            The request parameters.
	 * @param headers
	 *            The request headers.
	 * @my.headers <pre>
	 * 1.<strong>Range</strong>.Optional range of data to retrieve
	 * 2.<strong>If-Range</strong>.Retrieve the missing part if entity is unchanged; otherwise,retrieve the entire new entity (used together with Range header)
	 * 3.<strong>If-Match</strong>.Retrieve if ETags match
	 * 4.<strong>If-None-Match</strong>.Retrieve if ETags don’t match
	 * 5.<strong>If-Modified-Since</strong>.Retrieve if object has changed since provided timestamp
	 * 6.<strong>If-Unmodified-Since</strong>.Retrieve if object has not changed since provided timestamp
	 * </pre>
	 * @my.attributes <pre>
	 * 1.<strong>format</strong>.Optional extended reply type (can be json or xml)
	 * 2.<strong>hashmap</strong>.Optional request for hashmap (no value parameter)
	 * 3.<strong>version</strong>.Optional version identifier or list (specify a format if requesting a list)
	 * 4.<strong>disposition-type</strong>.Optional enforcement of the specific content disposition type
	 * 			(can be inline or attachment otherwise it is ignored - this will override the object’s Content-Disposition)
	 * </pre>
	 * @return The actual object,except if a hashmap is requested or a
	 *         version=list
	 * @throws IOException
	 * @example <pre>
	 * <strong>Download object info:</strong>
	 * PithosRESTAPI client = new PithosRESTAPI(url, token, username);
	 * HashMap<String, String> parameters = new HashMap<String, String>();
	 * HashMap<String, String> headers = new HashMap<String, String>();
	 * parameters.put("format", "json");
	 * System.out.println(client.read_object_data("object_name", "", parameters,headers));
	 * </pre>
	 * @example <pre>
	 * <strong>Download object :</strong>
	 * PithosRESTAPI client = new PithosRESTAPI(url, token, username);
	 * HashMap<String, String> parameters = new HashMap<String, String>();
	 * HashMap<String, String> headers = new HashMap<String, String>();
	 * parameters.put("format", "json");
	 * parameters.put("hashmap", "True");
	 * System.out.println(client.read_object_data("object_name", "", parameters,headers));
	 * </pre>
	 * @reply.headers <pre>
	 * 1.<strong>ETag</strong>.The ETag of the object
	 * 2.<strong>Content-Length</strong>.The size of the object
	 * 3.<strong>Content-Type</strong>.The MIME content type of the object
	 * 4.<strong>Last-Modified</strong>.The last object modification date (regardless of version)
	 * 5.<strong>Content-Encoding</strong>.The encoding of the object (optional)
	 * 6.<strong>Content-Disposition</strong>.The presentation style of the object (optional)
	 * 7.<strong>X-Object-Hash</strong>.The Merkle hash
	 * 8.<strong>X-Object-UUID</strong>.The object’s UUID
	 * 9.<strong>X-Object-Version</strong>.The object’s version identifier
	 * 10.<strong>X-Object-Version-Timestamp</strong>.The object’s version timestamp
	 * 11.<strong>X-Object-Modified-By</strong>.The user that comitted the object’s version
	 * 12.<strong>X-Object-Manifest</strong>.Object parts prefix in <container>/<object> form (optional)
	 * 13.<strong>X-Object-Sharing</strong>.Object permissions (optional)
	 * 14.<strong>X-Object-Shared-By</strong>.Object inheriting permissions (optional)
	 * 15.<strong>X-Object-Allowed-To</strong>.Allowed actions on object (optional)
	 * 16.<strong>X-Object-Public</strong>.Object’s publicly accessible URI (optional: present if the object is public and the request user is the object owner)
	 * 17.<strong>X-Object-Meta-*</strong>.Optional user defined metadata
	 * 18.<strong>Content-Range</strong>.The range of data included (only on a single range request)
	 * </pre>
	 * @return.code <pre>
	 * 200 (No Content) - The request succeeded
	 * 206 (Parial Content) - The range request succeeded
	 * 304 (Not Modified) - The object has not been modified
	 * 412 (Precondition Failed) - The condition set can not be satisfied
	 * 416 (Range Not Satisfiable) - The requested range is out of limits
	 * </pre>
	 */
	public Object read_object_data(String filename, String container,
			HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {
			if (container.equals("") || container == null)
				container = "pithos";

			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}
			String urlCloned = getUrl() + "/" + getUsername() + "/" + container
					+ "/" + filename;
			configureConnection(urlCloned, "GET", parameters, headers);
			System.out
					.println("Reading object:" + filename
							+ " of the account of user with token:"
							+ getX_Auth_Token());
			System.out.println("Sending 'GET' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();

			if (responseCode == 200 || responseCode == 206) {

				File outfile = null;

				if (parameters.containsKey("hashmap")
						|| (parameters.containsKey("version") && parameters
								.containsValue("list"))) {

					BufferedReader in = new BufferedReader(
							new InputStreamReader(this.getConnection()
									.getInputStream()));

					String inputLine;
					StringBuffer response = new StringBuffer();

					while ((inputLine = in.readLine()) != null) {
						response.append(inputLine);
					}
					in.close();
					System.out.println(getConnection().getHeaderFields());
					return response.toString();

				} else {
					InputStream inputStream = getConnection().getInputStream();
					if (filename.contains("/"))
						filename = filename.substring(
								filename.lastIndexOf("/") + 1,
								filename.length());

					outfile = new File(filename);
					OutputStream outputStream = new FileOutputStream(outfile);

					int read = 0;
					byte[] bytes = new byte[1024];

					while ((read = inputStream.read(bytes)) != -1) {
						outputStream.write(bytes, 0, read);
					}

					if (outputStream != null) {
						try {

							outputStream.close();

						} catch (IOException e) {
							e.printStackTrace();
							return null;
						}

					}

				}
				System.out.println(getConnection().getHeaderFields());
				return outfile;

			} else {
				System.err.println(responseCode);
				return null;
			}
		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * Delete a specific object
	 * 
	 * @param filename
	 *            The object name representation.
	 * 
	 * @param container
	 *            The container of the object(default is pithos called
	 *            container).
	 * @param parameters
	 *            The request parameters.
	 * 
	 * @param headers
	 *            The request headers.<br>
	 * @my.attributes <pre>
	 * 1.<strong>until</strong>.Optional timestamp
	 * 2.<strong>delimiter</strong>.Optional delete also objects starting with object’s path and delimiter
	 * </pre>
	 * @return The response code.No reply content/headers.
	 * @throws IOException
	 * @return.code <pre>
	 * 204 (No Content) - The request succeeded
	 * </pre>
	 */
	public String delete_object(String filename, String container,
			HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {
			if (container.equals("") || container == null)
				container = "pithos";

			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}
			String urlCloned = getUrl() + "/" + getUsername() + "/" + container
					+ "/" + filename;
			configureConnection(urlCloned, "DELETE", parameters, headers);
			System.out.println("Deleting the item:" + filename
					+ " of user with token:" + getX_Auth_Token());
			System.out.println("Sending 'DELETE' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();
			System.out.println(getConnection().getHeaderFields());
			return String.valueOf(responseCode);

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * Upload a file or create a folder object.
	 * 
	 * @param file2upload
	 *            If a string is provided then a folder is created,if a file
	 *            object is provided then it is uploaded.
	 * @param contentLength
	 *            The content length (zero for folder creation)
	 * @param container
	 *            The container of the object(default is pithos called
	 *            container).
	 * @param parameters
	 *            The request parameters.
	 * @param headers
	 *            The request headers.
	 * @my.headers <pre>
	 * 1.<strong>If-Match</strong>.Put if ETags match with current object
	 * 2.<strong>If-None-Match</strong>.Put if ETags don’t match with current object
	 * 3.<strong>ETag</strong>.The MD5 hash of the object (optional to check written data)
	 * 4.<strong>Content-Length</strong>.The size of the data written
	 * 5.<strong>Content-Type</strong>.The MIME content type of the object
	 * 6.<strong>Transfer-Encoding</strong>.Set to chunked to specify incremental uploading (if used, Content-Length is ignored)
	 * 7.<strong>X-Copy-From</strong>.The source path in the form /<container>/<object>
	 * 8.<strong>X-Move-From</strong>.The source path in the form /<container>/<object>
	 * 9.<strong>X-Source-Account</strong>.The source account to copy/move from
	 * 10.<strong>X-Source-Version</strong>.The source version to copy from
	 * 11.<strong>Content-Encoding</strong>.The encoding of the object (optional)
	 * 12.<strong>Content-Disposition</strong>.The presentation style of the object (optional)
	 * 13.<strong>X-Object-Manifest</strong>.Object parts prefix in <container>/<object> form (optional)
	 * 14.<strong>X-Object-Sharing</strong>.Object permissions (optional)
	 * 15.<strong>X-Object-Public</strong>.Object is publicly accessible (optional)
	 * 16.<strong>X-Object-Meta-*</strong>.Optional user defined metadata
	 * </pre>
	 * @my.attributes <pre>
	 * 1.<strong>format</strong>.Optional extended request/conflict response type (obsolete: always json is assumed)
	 * 1.<strong>hashmap</strong>.Optional hashmap provided instead of data (no value parameter)
	 * 1.<strong>delimiter</strong>.Optional copy/move objects starting with object’s path and delimiter (to be used with X-Copy-From/X-Move-From)
	 * </pre>
	 * @example <strong>Upload file:</strong>
	 * 
	 *          <pre>
	 * PithosRESTAPI client = new PithosRESTAPI(url, token, username);
	 * HashMap&lt;String, String&gt; parameters = new HashMap&lt;String, String&gt;();
	 * HashMap&lt;String, String&gt; headers = new HashMap&lt;String, String&gt;();
	 * headers.put(&quot;Content-Type&quot;, &quot;text/plain&quot;);
	 * System.out.println(client.upload_file(new File(&quot;a_text_file&quot;), null, &quot;&quot;,
	 * 		parameters, headers));
	 * </pre>
	 * @example <strong>Create a folder:</strong>
	 * 
	 *          <pre>
	 * PithosRESTAPI client = new PithosRESTAPI(url, token, username);
	 * HashMap&lt;String, String&gt; parameters = new HashMap&lt;String, String&gt;();
	 * HashMap&lt;String, String&gt; headers = new HashMap&lt;String, String&gt;();
	 * System.out.println(client
	 * 		.upload_file(&quot;testfolder&quot;, &quot;&quot;, &quot;&quot;, parameters, headers));
	 * </pre>
	 * @reply.headers <pre>
	 * 1.<strong>ETag</strong>.The MD5 (or the Merkle if MD5 is deactivated) hash of the object
	 * 2.<strong>X-Object-Version</strong>.The object’s new version
	 * </pre>
	 * @return Reponse code.
	 * @throws IOException
	 * @return.code <pre>
	 * 201 (Created) - The object has been created
	 * 403 (Forbidden) - If X-Copy-From and the source object is not available in the storage backend.
	 * 409 (Conflict) - The object can not be created from the provided hashmap (a list of missing hashes will be included in the reply)
	 * 411 (Length Required) - Missing Content-Length or Content-Type in the request
	 * 413 (Request Entity Too Large) - Insufficient quota to complete the request
	 * 422 (Unprocessable Entity) - The MD5 (or the Merkle if MD5 is deactivated) checksum of the data written
	 * 	   to the storage system does not match the (optionally) supplied ETag value
	 * </pre>
	 */
	@SuppressWarnings("unused")
	public String upload_file(Object file2upload, String contentLength,
			String container, HashMap<String, String> parameters,
			HashMap<String, String> headers) throws IOException {

		if (checkConf()) {
			if (container.equals("") || container == null)
				container = "pithos";

			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}

			String urlCloned = getUrl() + "/" + getUsername() + "/" + container
					+ "/";
			if (file2upload instanceof File) {

				File f2uload = (File) file2upload;
				urlCloned += f2uload.getName();

				configureConnection(urlCloned, "PUT", parameters, headers);

				if (contentLength != null) {
					if (contentLength.equals(""))
						this.getConnection().setFixedLengthStreamingMode(0);
					else {

						int clength = Integer.parseInt(contentLength);
						if (clength < 0) {
							System.err
									.println("Conten-Length should be greater to zero when uploading a file.");
							return null;
						}
						if (clength > 0)
							this.getConnection().setFixedLengthStreamingMode(
									clength);
						if (clength == 0) {
							System.err
									.println("Content-Length must be greater than zero when uploading a file.");
							return null;
						}
					}
				}

				this.getConnection().setDoOutput(true);

				if (file2upload != null) {

					System.out.println("Uploading file:" + f2uload.getName()
							+ " of user with token:" + getX_Auth_Token());
					System.out.println("Sending 'PUT' request to URL : "
							+ getUrl());

					int read = 0;
					byte[] bytes = new byte[1024];

					OutputStream outputStream = this.getConnection()
							.getOutputStream();
					FileInputStream fileInputStream = new FileInputStream(
							f2uload);

					while ((read = fileInputStream.read(bytes)) != -1) {
						outputStream.write(bytes, 0, read);
					}
					fileInputStream.close();

					int responseCode = getConnection().getResponseCode();
					System.out.println(getConnection().getHeaderFields());
					return String.valueOf(responseCode);

				}
				return null;

			} else if (file2upload instanceof String) {

				String folderName = (String) file2upload;
				urlCloned += folderName;
				headers.put("Content-Type", "application/directory");
				configureConnection(urlCloned, "PUT", parameters, headers);
				if (contentLength != null) {
					if (contentLength.equals(""))
						this.getConnection().setFixedLengthStreamingMode(0);
					else {

						int clength = Integer.parseInt(contentLength);
						if (clength < 0) {
							System.err
									.println("Conten-Length should be greater to zero.");
							return null;
						}
						if (clength > 0)
							this.getConnection().setFixedLengthStreamingMode(
									clength);
						if (clength == 0)
							this.getConnection().setFixedLengthStreamingMode(0);
					}
				}
				this.getConnection().setDoOutput(true);

				System.out.println("Creating folder:" + folderName
						+ " of user with token:" + getX_Auth_Token());
				System.out
						.println("Sending 'PUT' request to URL : " + getUrl());
				int responseCode = getConnection().getResponseCode();
				System.out.println(getConnection().getHeaderFields());
				return String.valueOf(responseCode);

			} else
				return null;

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * Copy an object
	 * 
	 * @param fromcontainer
	 *            The source container
	 * @param filename
	 *            The source object
	 * @param toContainer
	 *            The target container
	 * @param toFilename
	 *            The target object name
	 * @param parameters
	 *            Request parameters
	 * @param headers
	 *            Request headers
	 * @my.attributes <pre>
	 * 1.<strong>format</strong>.Optional extended request/conflict response type (obsolete: always json is assumed)
	 * 2.<strong>hashmap</strong>.Optional hashmap provided instead of data (no value parameter)
	 * 3.<strong>delimiter</strong>.Optional copy/move objects starting with object’s path and delimiter (to be used with X-Copy-From/X-Move-From)
	 * </pre>
	 * @return Response code
	 * @throws IOException
	 * @return.code <pre>
	 * 201 (Created) - The object has been created
	 * 403 (Forbidden) - If X-Copy-From and the source object is not available in the storage backend.
	 * 409 (Conflict) - The object can not be created from the provided hashmap (a list of missing hashes will be included in the reply)
	 * 411 (Length Required) - Missing Content-Length or Content-Type in the request
	 * 413 (Request Entity Too Large) - Insufficient quota to complete the request
	 * 422 (Unprocessable Entity) - The MD5 (or the Merkle if MD5 is deactivated) checksum of the data written to the storage system
	 * 	   does not match the (optionally) supplied ETag value
	 * </pre>
	 */
	public String copy_object(String fromcontainer, String filename,
			String toContainer, String toFilename,
			HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {
			if (fromcontainer.equals("") || fromcontainer == null)
				fromcontainer = "pithos";

			if (toContainer.equals("") || toContainer == null)
				toContainer = "pithos";

			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}

			String to = getUrl() + "/" + getUsername() + "/" + toContainer
					+ "/" + toFilename;
			String from = "/" + fromcontainer + "/" + filename;

			headers.put("X-Copy-From", from);

			configureConnection(to, "PUT", parameters, headers);

			this.getConnection().setFixedLengthStreamingMode(0);

			this.getConnection().setDoOutput(true);

			System.out.println("Copying the item:" + from
					+ " of user with token:" + getX_Auth_Token() + " to:" + to);
			System.out.println("Sending 'PUT' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();
			System.out.println(getConnection().getHeaderFields());

			return String.valueOf(responseCode);

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * Move an object
	 * 
	 * @param fromcontainer
	 *            The source container
	 * @param filename
	 *            The source object
	 * @param toContainer
	 *            The target container
	 * @param toFilename
	 *            The target object name
	 * @param parameters
	 *            Request parameters
	 * @param headers
	 *            Request headers
	 * @my.attributes <pre>
	 * 1.<strong>format</strong>.Optional extended request/conflict response type (obsolete: always json is assumed)
	 * 2.<strong>hashmap</strong>.Optional hashmap provided instead of data (no value parameter)
	 * 3.<strong>delimiter</strong>.Optional copy/move objects starting with object’s path and delimiter (to be used with X-Copy-From/X-Move-From)
	 * </pre>
	 * @return Response code
	 * @throws IOException
	 * @return.code <pre>
	 * 201 (Created) - The object has been created
	 * 403 (Forbidden) - If X-Copy-From and the source object is not available in the storage backend.
	 * 409 (Conflict) - The object can not be created from the provided hashmap (a list of missing hashes will be included in the reply)
	 * 411 (Length Required) - Missing Content-Length or Content-Type in the request
	 * 413 (Request Entity Too Large) - Insufficient quota to complete the request
	 * 422 (Unprocessable Entity) - The MD5 (or the Merkle if MD5 is deactivated) checksum of the data written to the storage system
	 *    does not match the (optionally) supplied ETag value
	 * </pre>
	 */
	public String move_object(String fromcontainer, String filename,
			String toContainer, String toFilename,
			HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {
			if (fromcontainer.equals("") || fromcontainer == null)
				fromcontainer = "pithos";

			if (toContainer.equals("") || toContainer == null)
				toContainer = "pithos";

			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}

			String to = getUrl() + "/" + getUsername() + "/" + toContainer
					+ "/" + toFilename;
			String from = "/" + fromcontainer + "/" + filename;

			headers.put("X-Move-From", from);

			configureConnection(to, "PUT", parameters, headers);

			this.getConnection().setFixedLengthStreamingMode(0);

			this.getConnection().setDoOutput(true);

			System.out.println("Moving the item:" + from
					+ " of user with token:" + getX_Auth_Token() + " to:" + to);
			System.out.println("Sending 'PUT' request to URL : " + getUrl());
			int responseCode = getConnection().getResponseCode();

			System.out.println(getConnection().getHeaderFields());
			return String.valueOf(responseCode);

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * Update,append truncate object
	 * 
	 * @param container
	 *            The source container
	 * @param filename
	 *            The object to update,append,truncate
	 * @param content
	 *            The content to Update,append truncate object
	 * @param parameters
	 *            The request parameters
	 * @param headers
	 *            The request headers
	 * @my.attributes <pre>
	 * 1.<strong>format</strong>.Optional conflict response type (can be json or xml)
	 * 2.<strong>update</strong>.Do not replace metadata (no value parameter)
	 * </pre>
	 * @my.headers <pre>
	 * 1.<strong>If-Match</strong>.Put if ETags match with current object
	 * 2.<strong>If-None-Match</strong>.Put if ETags don’t match with current object
	 * 3.<strong>Content-Length</strong>.The size of the data written (optional, to update)
	 * 4.<strong>Content-Type</strong>.The MIME content type of the object (optional, to update)
	 * 5.<strong>Content-Range</strong>.The range of data supplied (optional, to update)
	 * 6.<strong>Transfer-Encoding</strong>.Set to chunked to specify incremental uploading (if used, Content-Length is ignored)
	 * 7.<strong>Content-Encoding</strong>.The encoding of the object (optional)
	 * 8.<strong>Content-Disposition</strong>.The presentation style of the object (optional)
	 * 9.<strong>X-Source-Object</strong>.Update with data from the object at path /<container>/<object> (optional, to update)
	 * 10.<strong>X-Source-Account</strong>.The source account to update from
	 * 11.<strong>X-Source-Version</strong>.The source version to update from (optional, to update)
	 * 12.<strong>X-Object-Bytes</strong>.The updated object’s final size (optional, when updating)
	 * 13.<strong>X-Object-Manifest</strong>.Object parts prefix in <container>/<object> form (optional)
	 * 14.<strong>X-Object-Sharing</strong>.Object permissions (optional)
	 * 15.<strong>X-Object-Public</strong>.Object is publicly accessible (optional)
	 * 16.<strong>X-Object-Meta-*</strong>.Optional user defined metadata
	 * </pre>
	 * @example <strong>Update file:</strong>
	 * 
	 *          <pre>
	 * PithosRESTAPI client = new PithosRESTAPI(url, token, username);
	 * HashMap<String, String> parameters = new HashMap<String, String>();
	 * HashMap<String, String> headers = new HashMap<String, String>();
	 * parameters.put("format", "json");
	 * <strong>headers.put("Content-Range", "bytes 10-19/*");</strong>
	 * System.out.println(client.update_append_truncate_object("","an_object", "0123456789", parameters,headers));
	 * </pre>
	 * @example <strong>Append file:</strong>
	 * 
	 *          <pre>
	 * PithosRESTAPI client = new PithosRESTAPI(url, token, username);
	 * HashMap<String, String> parameters = new HashMap<String, String>();
	 * HashMap<String, String> headers = new HashMap<String, String>();
	 * parameters.put("format", "json");
	 * <strong>headers.put("Content-Range", "bytes *\/*");</strong>
	 * System.out.println(client.update_append_truncate_object("","an_object", "0123456789", parameters,headers));
	 * </pre>
	 * @example <strong>Truncate file:</strong>
	 * 
	 *          <pre>
	 * PithosRESTAPI client = new PithosRESTAPI(url, token, username);
	 * HashMap<String, String> parameters = new HashMap<String, String>();
	 * HashMap<String, String> headers = new HashMap<String, String>();
	 * parameters.put("format", "json");
	 * <strong>headers.put("Content-Range", "bytes 0-12/*");</strong>
	 * <strong>headers.put("X-Object-Bytes", "12");</strong>
	 * System.out.println(client.update_append_truncate_object("","an_object", null, parameters, headers));
	 * </pre>
	 * 
	 * @return response code
	 * @throws IOException
	 * 
	 * @return.code <pre>
	 * 202 (Accepted) - The request has been accepted (not a data update)
	 * 204 (No Content) - The request succeeded (data updated)
	 * 400 (Bad Request) - nvalid X-Object-Sharing or X-Object-Bytes header or missing Content-Range header or invalid source object
	 *     or source object length is smaller than range length or Content-Length does not match range length
	 *     or the metadata exceed in number the allowed object metadata
	 * 411 (Length Required) - Missing Content-Length or Content-Type in the request
	 * 413 (Request Entity Too Large) - Insufficient quota to complete the request
	 * 416 (Range Not Satisfiable) - The supplied range is invalid
	 * </pre>
	 */

	public String update_append_truncate_object(String container,
			String filename, String content,

			HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {
			if (container.equals("") || container == null)
				container = "pithos";

			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}

			String urlCloned = getUrl() + "/" + getUsername() + "/" + container
					+ "/" + filename;

			headers.put("Content-Type", "application/octet-stream");

			if (content != null) {
				configureConnection(urlCloned, "POST", parameters, headers);
				this.getConnection().setDoOutput(true);
				DataOutputStream wr = new DataOutputStream(getConnection()
						.getOutputStream());
				wr.writeBytes(content);
				wr.flush();
				wr.close();
			} else {
				System.out.println("Truncating file:" + filename);

				headers.put("X-Source-Object", "/" + container + "/" + filename);
				configureConnection(urlCloned, "POST", parameters, headers);
				this.getConnection().setFixedLengthStreamingMode(0);
				this.getConnection().setDoOutput(true);
			}

			System.out.println("Updating the item:" + filename
					+ " of user with token:" + getX_Auth_Token());
			System.out.println("Sending 'POST' request to URL : " + getUrl());

			System.out.println(getConnection().getHeaderFields());
			int responseCode = getConnection().getResponseCode();

			return String.valueOf(responseCode);

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * Add custom object metadata.
	 * 
	 * @param container
	 *            The source container(pithos is the default)
	 * @param filename
	 *            The object to update,append,truncate
	 * @param parameters
	 *            The request parameters
	 * @param headers
	 *            The request headers
	 * 
	 * @my.attributes <pre>
	 * 1.<strong>format</strong>.Optional conflict response type (can be json or xml)
	 * 2.<strong>update</strong>.Do not replace metadata (no value parameter)
	 * </pre>
	 * @my.headers <pre>
	 * 1.<strong>If-Match</strong>.Put if ETags match with current object
	 * 2.<strong>If-None-Match</strong>.Put if ETags don’t match with current object
	 * 3.<strong>Content-Length</strong>.The size of the data written (optional, to update)
	 * 4.<strong>Content-Type</strong>.The MIME content type of the object (optional, to update)
	 * 5.<strong>Content-Range</strong>.The range of data supplied (optional, to update)
	 * 6.<strong>Transfer-Encoding</strong>.Set to chunked to specify incremental uploading (if used, Content-Length is ignored)
	 * 7.<strong>Content-Encoding</strong>.The encoding of the object (optional)
	 * 8.<strong>Content-Disposition</strong>.The presentation style of the object (optional)
	 * 9.<strong>X-Source-Object</strong>.Update with data from the object at path /<container>/<object> (optional, to update)
	 * 10.<strong>X-Source-Account</strong>.The source account to update from
	 * 11.<strong>X-Source-Version</strong>.The source version to update from (optional, to update)
	 * 12.<strong>X-Object-Bytes</strong>.The updated object’s final size (optional, when updating)
	 * 13.<strong>X-Object-Manifest</strong>.Object parts prefix in <container>/<object> form (optional)
	 * 14.<strong>X-Object-Sharing</strong>.Object permissions (optional)
	 * 15.<strong>X-Object-Public</strong>.Object is publicly accessible (optional)
	 * 16.<strong>X-Object-Meta-*</strong>.Optional user defined metadata
	 * </pre>
	 * 
	 * @example <strong>Add object metadata:</strong>
	 * 
	 *          <pre>
	 * PithosRESTAPI client = new PithosRESTAPI(url, token, username);
	 * HashMap<String, String> parameters = new HashMap<String, String>();
	 * HashMap<String, String> headers = new HashMap<String, String>();
	 * parameters.put("format", "json");
	 * <strong>>headers.put("X-Object-Meta-Owner", "Kostas Vogias");</strong>
	 * System.out.println(client.add_object_metadata("","an_object", parameters, headers));
	 * </pre>
	 * 
	 * @return Response code
	 * @throws IOException
	 * 
	 * @return.code <pre>
	 * 202 (Accepted) - The request has been accepted (not a data update)
	 * 204 (No Content) - The request succeeded (data updated)
	 * 400 (Bad Request) - nvalid X-Object-Sharing or X-Object-Bytes header or missing Content-Range header or invalid source object
	 *     or source object length is smaller than range length or Content-Length does not match range length
	 *     or the metadata exceed in number the allowed object metadata
	 * 411 (Length Required) - Missing Content-Length or Content-Type in the request
	 * 413 (Request Entity Too Large) - Insufficient quota to complete the request
	 * 416 (Range Not Satisfiable) - The supplied range is invalid
	 * </pre>
	 */
	public String add_object_metadata(String container, String filename,

	HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {
			if (container.equals("") || container == null)
				container = "pithos";

			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}

			String urlCloned = getUrl() + "/" + getUsername() + "/" + container
					+ "/" + filename;

			configureConnection(urlCloned, "POST", parameters, headers);

			System.out.println("Adding metadata to the item:" + filename
					+ " of user with token:" + getX_Auth_Token());
			System.out.println("Sending 'POST' request to URL : " + getUrl());

			System.out.println(getConnection().getHeaderFields());
			int responseCode = getConnection().getResponseCode();

			return String.valueOf(responseCode);

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * Make an object public
	 * 
	 * @param container
	 *            The source container(pithos is the default)
	 * @param filename
	 *            The object to update,append,truncate
	 * @param parameters
	 *            The request parameters
	 * @param headers
	 *            The request headers
	 * 
	 * @my.attributes <pre>
	 * 1.<strong>format</strong>.Optional conflict response type (can be json or xml)
	 * 2.<strong>update</strong>.Do not replace metadata (no value parameter)
	 * </pre>
	 * @my.headers <pre>
	 * 1.<strong>If-Match</strong>.Put if ETags match with current object
	 * 2.<strong>If-None-Match</strong>.Put if ETags don’t match with current object
	 * 3.<strong>Content-Length</strong>.The size of the data written (optional, to update)
	 * 4.<strong>Content-Type</strong>.The MIME content type of the object (optional, to update)
	 * 5.<strong>Content-Range</strong>.The range of data supplied (optional, to update)
	 * 6.<strong>Transfer-Encoding</strong>.Set to chunked to specify incremental uploading (if used, Content-Length is ignored)
	 * 7.<strong>Content-Encoding</strong>.The encoding of the object (optional)
	 * 8.<strong>Content-Disposition</strong>.The presentation style of the object (optional)
	 * 9.<strong>X-Source-Object</strong>.Update with data from the object at path /<container>/<object> (optional, to update)
	 * 10.<strong>X-Source-Account</strong>.The source account to update from
	 * 11.<strong>X-Source-Version</strong>.The source version to update from (optional, to update)
	 * 12.<strong>X-Object-Bytes</strong>.The updated object’s final size (optional, when updating)
	 * 13.<strong>X-Object-Manifest</strong>.Object parts prefix in <container>/<object> form (optional)
	 * 14.<strong>X-Object-Sharing</strong>.Object permissions (optional)
	 * 15.<strong>X-Object-Public</strong>.Object is publicly accessible (optional)
	 * 16.<strong>X-Object-Meta-*</strong>.Optional user defined metadata
	 * </pre>
	 * @return Response code
	 * @throws IOException
	 * 
	 * @return.code <pre>
	 * 202 (Accepted) - The request has been accepted (not a data update)
	 * 204 (No Content) - The request succeeded (data updated)
	 * 400 (Bad Request) - nvalid X-Object-Sharing or X-Object-Bytes header or missing Content-Range header or invalid source object
	 * or source object length is smaller than range length or Content-Length does not match range length or the metadata exceed in number the allowed object metadata
	 * 411 (Length Required) - Missing Content-Length or Content-Type in the request
	 * 413 (Request Entity Too Large) - Insufficient quota to complete the request
	 * 416 (Range Not Satisfiable) - The supplied range is invalid
	 * </pre>
	 */

	public String publish_object(String container, String filename,

	HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {
			if (container.equals("") || container == null)
				container = "pithos";

			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}

			String urlCloned = getUrl() + "/" + getUsername() + "/" + container
					+ "/" + filename;

			headers.put("X-Object-Public", "True");
			configureConnection(urlCloned, "POST", parameters, headers);

			System.out.println("Publishing the item:" + filename
					+ " of user with token:" + getX_Auth_Token());
			System.out.println("Sending 'POST' request to URL : " + getUrl());

			System.out.println(getConnection().getHeaderFields());
			int responseCode = getConnection().getResponseCode();

			return String.valueOf(responseCode);

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}

	/**
	 * Make an object private
	 * 
	 * 
	 * @param container
	 *            The source container(pithos is the default)
	 * @param filename
	 *            The object to update,append,truncate
	 * @param parameters
	 *            The request parameters
	 * @param headers
	 *            The request headers
	 * @my.attributes <pre>
	 * 1.<strong>format</strong>.Optional conflict response type (can be json or xml)
	 * 2.<strong>update</strong>.Do not replace metadata (no value parameter)
	 * </pre>
	 * @my.headers <pre>
	 * 1.<strong>If-Match</strong>.Put if ETags match with current object
	 * 2.<strong>If-None-Match</strong>.Put if ETags don’t match with current object
	 * 3.<strong>Content-Length</strong>.The size of the data written (optional, to update)
	 * 4.<strong>Content-Type</strong>.The MIME content type of the object (optional, to update)
	 * 5.<strong>Content-Range</strong>.The range of data supplied (optional, to update)
	 * 6.<strong>Transfer-Encoding</strong>.Set to chunked to specify incremental uploading (if used, Content-Length is ignored)
	 * 7.<strong>Content-Encoding</strong>.The encoding of the object (optional)
	 * 8.<strong>Content-Disposition</strong>.The presentation style of the object (optional)
	 * 9.<strong>X-Source-Object</strong>.Update with data from the object at path /<container>/<object> (optional, to update)
	 * 10.<strong>X-Source-Account</strong>.The source account to update from
	 * 11.<strong>X-Source-Version</strong>.The source version to update from (optional, to update)
	 * 12.<strong>X-Object-Bytes</strong>.The updated object’s final size (optional, when updating)
	 * 13.<strong>X-Object-Manifest</strong>.Object parts prefix in <container>/<object> form (optional)
	 * 14.<strong>X-Object-Sharing</strong>.Object permissions (optional)
	 * 15.<strong>X-Object-Public</strong>.Object is publicly accessible (optional)
	 * 16.<strong>X-Object-Meta-*</strong>.Optional user defined metadata
	 * </pre>
	 * 
	 * @return Response code
	 * @throws IOException
	 * 
	 * @return.code <pre>
	 * 202 (Accepted) - The request has been accepted (not a data update)
	 * 204 (No Content) - The request succeeded (data updated)
	 * 400 (Bad Request) - nvalid X-Object-Sharing or X-Object-Bytes header or missing Content-Range header or invalid source object
	 * or source object length is smaller than range length or Content-Length does not match range length or the metadata exceed in number the allowed object metadata
	 * 411 (Length Required) - Missing Content-Length or Content-Type in the request
	 * 413 (Request Entity Too Large) - Insufficient quota to complete the request
	 * 416 (Range Not Satisfiable) - The supplied range is invalid
	 * </pre>
	 * 
	 */
	public String unpublish_object(String container, String filename,

	HashMap<String, String> parameters, HashMap<String, String> headers)
			throws IOException {

		if (checkConf()) {
			if (container.equals("") || container == null)
				container = "pithos";

			if (getUsername().equals("")) {
				System.err.println("Username is not defined.");
				return null;
			}

			String urlCloned = getUrl() + "/" + getUsername() + "/" + container
					+ "/" + filename;

			headers.put("X-Object-Public", "False");
			configureConnection(urlCloned, "POST", parameters, headers);

			System.out.println("Publishing the item:" + filename
					+ " of user with token:" + getX_Auth_Token());
			System.out.println("Sending 'POST' request to URL : " + getUrl());

			System.out.println(getConnection().getHeaderFields());
			int responseCode = getConnection().getResponseCode();

			return String.valueOf(responseCode);

		} else

		{
			System.err.println("ERROR: X-Auth-Token is empty");
			return null;
		}

	}
}
