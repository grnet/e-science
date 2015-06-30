package tests;

import gr.grnet.escience.commons.Utils;
import gr.grnet.escience.pithos.rest.HadoopPithosConnector;

import java.io.IOException;

import org.junit.BeforeClass;
import org.junit.Test;

public class TestPithosFileStatus {

    private static final String PITHOS_STORAGE_SYSTEM_URL = "https://pithos.okeanos.grnet.gr/v1";
    private static final String UUID = "ec567bea-4fa2-433d-9935-261a0867ec60";
    private static final String TOKEN = "n4kvgYT_8TEe8lwcWmOspulv5eZbyeBaSokmW6IfIQo";
    private static final String PITHOS_CONTAINER = "pithos";
    private static HadoopPithosConnector hdconnector;
    private static boolean dirFlag = false;
    private static String[] pithosObjectsArray;

    public TestPithosFileStatus() {
        createHdConnector();
    }

    @BeforeClass
    public static void createHdConnector() {
        // - CREATE HADOOP CONNECTOR INSTANCE
        if (hdconnector == null) {
            hdconnector = new HadoopPithosConnector(PITHOS_STORAGE_SYSTEM_URL,
                    TOKEN, UUID);
        }
    }

    @Test
    public void testPithos_File_List(String pithosFileListStr) {

        pithosObjectsArray = Utils.extractObjectList(pithosFileListStr, "\n");
        System.out
                .println("---------------------------------------------------------------------");
        System.out.println("LIST OF AVAILABLE OBJECTS ON CONTAINER:<"
                + PITHOS_CONTAINER + ">]");
        System.out
                .println("---------------------------------------------------------------------");
        for (String file : pithosObjectsArray)
            System.out.println(file);
        System.out
                .println("---------------------------------------------------------------------\n");
    }

    @Test
    public void testIsDir(String targetObject) {
        // - GET OBJECT ACTUAL SIZE
        System.out
                .println("---------------------------------------------------------------------");
        System.out.println("CHECH OBJECT: [OBJECT:<" + targetObject + ">]");
        System.out
                .println("---------------------------------------------------------------------");
        dirFlag = Utils.isDirectory(PITHOS_CONTAINER, targetObject, hdconnector);

        if (dirFlag) {
            System.out.println("[OBJECT:<" + targetObject
                    + ">] IS DIRECTORY/FOLDER.");
        } else {
            System.out.println("[OBJECT:<" + targetObject
                    + ">] IS NOT DIRECTORY/FOLDER.");
        }
        System.out
                .println("---------------------------------------------------------------------\n");
    }

    /**
     * @param args
     * @throws IOException
     * 
     */
    public static void main(String[] args) throws IOException {
        TestPithosFileStatus client = new TestPithosFileStatus();

        client.testPithos_File_List(hdconnector.getFileList(PITHOS_CONTAINER));

        for (String currentObj : pithosObjectsArray) {
            client.testIsDir(currentObj);
        }

    }

}
