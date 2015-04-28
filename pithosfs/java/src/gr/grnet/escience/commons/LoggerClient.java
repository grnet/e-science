package gr.grnet.escience.commons;

import org.graylog2.syslog4j.Syslog;
import org.graylog2.syslog4j.SyslogIF;

public class LoggerClient {

    private SyslogIF client = null;

    public LoggerClient() {
        // - Initialize client
        this.client = Syslog.getInstance(getLoggerServerDefaultProtocol());
        getClient().getConfig().setHost(getLoggerServerDefaultIP());
        getClient().getConfig().setPort(
                Integer.parseInt(getLoggerServerDefaultPort()));

        // - Info
        System.out.println("LOGGER CLIENT INITIALIZED SUCCESSFULLY:\n"
                + "\tProtocol: " + getClient().getProtocol() + "\n"
                + "\tHost: " + getClient().getConfig().getHost() + "\n"
                + "\tPort: " + getClient().getConfig().getPort() + "\n");
    }

    public LoggerClient(String loogerServerIp, String loggerServerPort,
            String loggerServerProtocol) {
        // - Initialize client
        this.client = Syslog.getInstance(loggerServerProtocol);
        getClient().getConfig().setHost(loogerServerIp);
        getClient().getConfig().setPort(Integer.parseInt(loggerServerPort));

        // - Info
        System.out.println("LOGGER CLIENT INITIALIZED SUCCESSFULLY:\n"
                + "\tProtocol: " + getClient().getProtocol() + "\n"
                + "\tHost: " + getClient().getConfig().getHost() + "\n"
                + "\tPort: " + getClient().getConfig().getPort() + "\n");
    }

    private String getLoggerServerDefaultIP() {
        // TODO: return the value as it is defined in XML core-site.xml
        return "192.168.0.2";
    }

    private String getLoggerServerDefaultPort() {
        // TODO: return the value as it is defined in XML core-site.xml
        return "1050";
    }

    private String getLoggerServerDefaultProtocol() {
        // TODO: return the value as it is defined in XML core-site.xml
        return "udp";
    }

    public SyslogIF getClient() {
        return client;
    }

}
