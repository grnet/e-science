package tests;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.URI;
import java.net.URISyntaxException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IOUtils;
import org.apache.hadoop.util.Progressable;

public class DataProcessor {
  public static void main(String[] args) throws IOException, URISyntaxException 
   {
      //1. Get the instance of COnfiguration
      Configuration configuration = new Configuration();
      configuration.get("fs.default.name", "pithos://");
      //2. Create an InputStream to read the data from local file
      InputStream inputStream = new BufferedInputStream(new FileInputStream("/home/everyones/workspace/input_data/input_file_01.txt"));
      //3. Get the HDFS instance
      FileSystem hdfs = FileSystem.get(new URI("hdfs://83.212.96.12:9000"), configuration);
      //4. Open a OutputStream to write the data, this can be obtained from the FileSytem
      OutputStream outputStream = hdfs.create(new Path("/home/hduser/hello/output.txt"),
      new Progressable() {  
              @Override
			public void progress() {
         System.out.println("....");
              }
                    });
      try
      {
        IOUtils.copyBytes(inputStream, outputStream, 4096, true); 
      }
      finally
      {
        IOUtils.closeStream(inputStream);
        IOUtils.closeStream(outputStream);
      } 
  }
}