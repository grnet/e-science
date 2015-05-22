package tests;

import gr.grnet.escience.commons.LoggerClient;

public class TestLogger {

    public TestLogger() {
        // TODO Auto-generated constructor stub
    }

    public static void main(String[] args) {
        LoggerClient loggerClient = new LoggerClient("192.168.0.2", "1050", "udp");

        loggerClient.getClient().alert("This is an ALERT message");
        loggerClient.getClient().critical("This is a CRITICAL message");
        loggerClient.getClient().debug("This is a DEBUG message");
        loggerClient.getClient().error("THis is an ERROR message");

    }

}
