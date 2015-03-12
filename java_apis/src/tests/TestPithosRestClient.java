package tests;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import org.orka.hadoop.pithos.rest.HadoopPithosRestConnector;

public class TestPithosRestClient {

	/**
	 * @param args
	 * @throws IOException
	 */
	public static void main(String[] args) throws IOException {
		HadoopPithosRestConnector hdconnector = new HadoopPithosRestConnector();

		// - Get the meta of the object
		Map<String, List<String>> metadata = hdconnector
				.getPithosObjectMetadata("", "test/Stage.rar");

		for (String meta_property_name : metadata.keySet()) {
			// - Get Property name
			System.out.println("Property: " + meta_property_name);
			for (String meta_property_value : metadata.get(meta_property_name)) {
				System.out.println("\t" + meta_property_value);
			}

		}

		// - Get the object & TODO: convert it into bytes and the stream it on a
		// file so as to be temporarily stored
		//hdconnector.getPithosObject("", "test/Stage.rar");

	}

}
