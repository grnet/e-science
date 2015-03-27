package tests;

import gr.grnet.escience.hdfs.client.OrkaHdfsClient;

import java.io.IOException;

@SuppressWarnings("unused")
public class TestHdfsClient {

	private static final String SOURCE_FILE = "";
	private static final String DESTINATION_FILE = "/user/hdfs/file_name";
	private static final String DIR_NAME = "";

	/**
	 * @param args
	 * @throws InterruptedException
	 * @throws IOException
	 */
	public static void main(String[] args) throws IOException,
			InterruptedException {

		//- Create client instance
		OrkaHdfsClient hdfsClient = new OrkaHdfsClient();
		
		// -1: COPY FROM LOCAL --> HDFS  
//		hdfsClient.copyFromLocalToHdfs(SOURCE_FILE, DESTINATION_FILE);

		// -2: COPY FROM HDFS --> LOCAL
//		hdfsClient.downloadFromHdfs(SOURCE_FILE, DESTINATION_FILE);

		// -3: UPLOAD DATA FROM LOCAL FILE TO HDFS FILE BY DATASTREAMING
//		hdfsClient.uploadToHdfs(SOURCE_FILE, DESTINATION_FILE);

		// -4: READ FILE CONTENTS FROM HDFS
//		hdfsClient.readFromHdfs(SOURCE_FILE);

		// -5: RENAME A FILE INTO HDFS
//		hdfsClient.renameFile(SOURCE_FILE, "new_name");

		// -6: CREATE DIRECTORY INTO HDFS
//		hdfsClient.mkdir(DIR_NAME);

		//-7: GET FILE BLOCKS LOCATION ON HDFS
//		hdfsClient.getBlockLocations(SOURCE_FILE);
		
		// -8: DELETE FILE FROM HDFS
//		hdfsClient.deleteFromHdfs(SOURCE_FILE);

	}

}
