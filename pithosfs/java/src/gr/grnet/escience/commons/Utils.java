package gr.grnet.escience.commons;

import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URLEncoder;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Utils {
    private static final boolean DEBUG = false;
    private LoggerClient loggerClient = new LoggerClient();
    private StringBuilder logStrBuilder = null;

    public Utils() {
    }

    /**
     * Fix the hash algorithm name
     * 
     * @param hashAlgorithm
     * @return unsquelch pithos X-Container-Block-Hash data
     */
    public String fixPithosHashName(String hashAlgorithm) {
        Pattern pSha = Pattern.compile("^(sha)([0-9]+)$",
                Pattern.CASE_INSENSITIVE);
        Matcher mSha = pSha.matcher(hashAlgorithm);
        if (mSha.matches()) {
            hashAlgorithm = String
                    .format("%s-%s", mSha.group(1), mSha.group(2));
        }
        return hashAlgorithm;
    }

    /**
     * Get the hash container
     * 
     * @param byteData
     *            : the byte array to get the digest of
     * @param hashAlgorithm
     *            : the name of the hash algorithm to use
     * @return bytestring hash representation of the input digest
     */
    public String computeHash(byte[] byteData, String hashAlgorithm)
            throws NoSuchAlgorithmException, UnsupportedEncodingException {
        /** eg. hash_algorithm = "SHA-256"; */
        MessageDigest digest = MessageDigest.getInstance(hashAlgorithm);
        digest.reset();

        byte[] byteDatad = digest.digest(byteData);
        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < byteDatad.length; i++) {
            sb.append(Integer.toString((byteDatad[i] & 0xff) + 0x100, 16)
                    .substring(1));
        }
        return sb.toString();
    }

    /**
     * Get the hash container
     * 
     * @param utf
     *            -8 string : the string to get the digest of
     * @param hashAlgorithm
     *            : the name of the hash algorithm to use
     * @return bytestring hash representation of the input digest
     */
    public String computeHash(String input, String hashAlgorithm)
            throws NoSuchAlgorithmException, UnsupportedEncodingException {
        /** eg. hash_algorithm = "SHA-256"; */
        MessageDigest digest = MessageDigest.getInstance(hashAlgorithm);
        digest.reset();

        byte[] byteData = digest.digest(input.getBytes("UTF-8"));
        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < byteData.length; i++) {
            sb.append(Integer.toString((byteData[i] & 0xff) + 0x100, 16)
                    .substring(1));
        }
        return sb.toString();
    }

    /**
     * Return an escaped url using form encoding and character replacement
     * 
     * @param url
     * @return url escaped path
     * @throws UnsupportedEncodingException
     */
    public String urlEscape(String url) throws UnsupportedEncodingException {
        return URLEncoder.encode(url, "UTF-8").replaceAll("\\+", "%20")
                .replaceAll("\\%21", "!").replaceAll("\\%27", "'")
                .replaceAll("\\%28", "(").replaceAll("\\%29", ")")
                .replaceAll("\\%7E", "~");
    }

    /**
     * Construct a URI from passed components and return the escaped and encoded
     * url
     * 
     * @param scheme
     *            : can be null for partial path
     * @param host
     *            : can be null for partial path
     * @param path
     * @param fragment
     *            : can be null for partial path
     * @return url escaped path
     * @throws URISyntaxException
     */
    public String urlEscape(String scheme, String host, String path,
            String fragment) throws URISyntaxException {
        URI uri = new URI(scheme, host, path, fragment);
        return uri.toASCIIString();
    }

    public static String getCurrentTimestamp() {
        // - Create and return a unique timestamp
        LocalDateTime ldt = LocalDateTime.now();
        DateTimeFormatter dtf = DateTimeFormatter.ISO_LOCAL_DATE_TIME;
        return ldt.format(dtf);
    }

    /**
     * Convert dateTime String to long epoch time in milliseconds
     * 
     * @param dtString
     *            : datetime as String invalid datetime string will use current
     *            datetime
     * @param dtFormat
     *            : DateTimeFormatter or String pattern to instantiate one pass
     *            empty string to use default
     * @return long epoch time in milliseconds
     */
    public Long dateTimeToEpoch(String dtString, Object dtFormat) {
        DateTimeFormatter dtf = null;
        Long epoch = null;
        if (dtFormat instanceof String) {
            if (dtFormat.toString() != "") {
                try {
                    dtf = DateTimeFormatter.ofPattern(dtFormat.toString());
                } catch (IllegalArgumentException ex) {
                    dtf = DateTimeFormatter.RFC_1123_DATE_TIME;
                    this.dbgPrint(
                            "dateTimeToEpoch: invalid DateFormatter pattern",
                            ex);
                }
            } else {
                dtf = DateTimeFormatter.RFC_1123_DATE_TIME;
            }

        } else if (dtFormat instanceof DateTimeFormatter) {
            dtf = (DateTimeFormatter) dtFormat;
        }
        try {
            LocalDateTime ldt = LocalDateTime.parse(dtString, dtf);
            ZonedDateTime zdt = ldt.atZone(ZoneId.systemDefault());
            epoch = zdt.toInstant().toEpochMilli();
        } catch (DateTimeParseException ex) {
            epoch = System.currentTimeMillis();
            this.dbgPrint(
                    "dateTimeToEpoch: invalid datetime string using current.",
                    ex, epoch);
        }
        return epoch;
    }

    /**
     * Thin wrapper around System.err.println for quick tracing
     * 
     * @param args
     *            : variable length array of objects
     */
    public void dbgPrint(Object... args) {
        if (!DEBUG) {
            return;
        }
        String formatter = "DEBUG:";
        for (int i = 0; i < args.length; i++) {
            formatter += " %s";
        }

        // -
        System.err.format(formatter + "\n", args);

        // - Create builder
        logStrBuilder = new StringBuilder(String.format(formatter, args));

        // - Write to centralized logger
        loggerClient.getClient().debug(logStrBuilder.toString());

    }

}
