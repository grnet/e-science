package tests;

import gr.grnet.escience.pithos.restapi.PithosRESTAPI;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.HashMap;
import java.util.Properties;

import org.junit.Before;
import org.junit.Test;

public class PithosClientTest {

	private String url, token, username;

	@Before
	public void prepareAttributes() throws FileNotFoundException, IOException {
		Properties props = new Properties();
		props.load(new FileInputStream("testMainAttributes.properties"));
		token = props.getProperty("token");
		username = props.getProperty("username");
		url = props.getProperty("url");
	}

	@Test
	public void testList_sharing_accounts() throws IOException {

		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();

		parameters.put("format", "json");

		HashMap<String, String> headers = new HashMap<String, String>();

		System.out.println(client.list_sharing_accounts(parameters, headers));

	}

	@Test
	public void testList_sharing_accounts_with_headers() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();

		parameters.put("format", "json");

		HashMap<String, String> headers = new HashMap<String, String>();

		headers.put("X-Auth-User", "auth_user");
		headers.put("X-Auth-Key", "auth_key");

		System.out.println(client.list_sharing_accounts(parameters, headers));

	}

	@Test
	public void testAccount_info() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		System.out.println(client.account_info(

		parameters, headers));

	}

	@Test
	public void testAccount_list_containers() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");
		// parameters.put("shared", "");
		// parameters.put("public", "");
		System.out.println(client.list_account_containers(

		parameters, headers));

	}

	@Test
	public void testUpdate_account_metadata() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		// parameters.put("shared", "");
		// parameters.put("public", "");
		System.out.println(client.update_account_metadata(

		parameters, headers));

	}

	@Test
	public void testRetrieve_container_info() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		System.out.println(client.retrieve_container_info("pithos", parameters,
				headers));

	}

	@Test
	public void testList_container_objects() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");
	//	parameters.put("public", "");

		System.out.println(client.list_container_objects("pithos", parameters,
				headers));

	}

	@Test
	public void testCreate_update_account_container() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		System.out.println(client.create_update_container("test2", parameters,
				headers));

	}

	@Test
	public void testUpdate_container_metadata() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");
		System.out.println(client.update_container_metadata("test2",
				parameters, headers));

	}

	@Test
	public void testDelete_container() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");
		System.out
				.println(client.delete_container("test2", parameters, headers));

	}

	@Test
	public void testRetrieve_object_metadata() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");
		System.out.println(client.retrieve_object_metadata("RSSReader.rar", "",
				parameters, headers));

	}

	@Test
	public void testRead_object_data() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");

		// retrieve object hash representation
		 parameters.put("hashmap", "True");

		// parameters.put("version", "list");
		// headers.put("Range", "bytes=0-9");
		System.out
				.println(client.read_object_data(
						"AriadneID/AriadneIdentification.rar", "", parameters,
						headers));

	}

	@Test
	public void testDelete_object() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		
		System.out.println(client
				.delete_object("testMainAttributes.properties", "", parameters, headers));

	}

	@Test
	public void testCreate_Folder() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		// parameters.put("format", "json");
		// parameters.put("hashmap", "True");
		// parameters.put("version", "list");
		// headers.put("Range", "bytes=0-9");

		// System.out.println(client.create_folder("testfolder", "", parameters,
		// headers));
		System.out.println(client.upload_file("testfolder", "", "", parameters,
				headers));

	}

	@Test
	public void testUpload_file() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		// parameters.put("format", "json");
		// parameters.put("hashmap", "True");
		// parameters.put("version", "list");
		// headers.put("Range", "bytes=0-9");

		headers.put("Content-Type", "text/plain");

		System.out.println(client
				.upload_file(new File("testMainAttributes.properties"), null,
						"", parameters, headers));

	}

	@Test
	public void testCopy_file() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");

		// headers.put("Content-Type", "text/plain");

		// System.out.println(client.copy_object("",
		// "testMainAttributes.properties", "test2",
		// "Backup/testMainAttributes.properties", parameters, headers));
		System.out.println(client.copy_object("",
				"testMainAttributes.properties", "",
				"Backup/testMainAttributes.properties", parameters, headers));

	}

	@Test
	public void testMove_file() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");

		// headers.put("Content-Type", "text/plain");

		System.out.println(client.move_object("",
				"testMainAttributes.properties", "",
				"Backup/testMainAttributes.properties", parameters, headers));

	}

	@Test
	public void testUpdate_Object() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");

		// update an object
		headers.put("Content-Range", "bytes 10-19/*");

		System.out.println(client.update_append_truncate_object("",
				"testMainAttributes.properties", "0123456789", parameters,
				headers));
	}

	@Test
	public void testAppend_Object() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");

		// append
		headers.put("Content-Range", "bytes */*");

		System.out.println(client.update_append_truncate_object("",
				"testMainAttributes.properties", "0123456789", parameters,
				headers));
	}

	@Test
	public void testTruncate_Object() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");

		// truncate
		headers.put("Content-Range", "bytes 0-12/*");
		headers.put("X-Object-Bytes", "12");

		System.out.println(client.update_append_truncate_object("",
				"testMainAttributes.properties", null, parameters, headers));
	}

	@Test
	public void testAdd_Object_Metadata() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");

		headers.put("X-Object-Meta-Owner", "Kostas Vogias");

		System.out.println(client.add_object_metadata("",
				"testMainAttributes.properties", parameters, headers));
	}

	@Test
	public void testPublish_Object() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");

		System.out.println(client.publish_object("",
				"testMainAttributes.properties", parameters, headers));
	}

	@Test
	public void testUnpublish_Object() throws IOException {
		PithosRESTAPI client = new PithosRESTAPI(url, token, username);
		HashMap<String, String> parameters = new HashMap<String, String>();
		HashMap<String, String> headers = new HashMap<String, String>();

		parameters.put("format", "json");

		System.out.println(client.unpublish_object("",
				"testMainAttributes.properties", parameters, headers));
	}
}
