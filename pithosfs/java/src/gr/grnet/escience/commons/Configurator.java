package gr.grnet.escience.commons;

import gr.grnet.escience.fs.pithos.PithosFileSystem;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;

import org.apache.hadoop.fs.Path;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

/**
 * @since March, 2015
 * @author Dimitris G. Kelaidonis (kelaidonis@gmail.com)
 * @version 0.1
 */
public class Configurator {

	private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
	
	/**
	 * Read setting Json file
	 * @param filename
	 */
	public static Settings load(String filename){
		try {
			String str = new String (Files.readAllBytes(Paths.get(new File(filename).toURI())), Charset.forName("UTF-8"));
	 		return GSON.fromJson(str, Settings.class);

		} catch (Throwable e) {
			e.printStackTrace();
			return null;
		}		
	}
	
	/**
	 * Create setting Json file
	 */
	public static void create(String filename, Settings settings) {
		String json = GSON.toJson(settings);
		try {
			File file = new File(filename);
			
			if (!file.exists()) {
				file.createNewFile();
			}
 
			//- Create the writer & append the contents
			Writer out = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(file), "UTF-8"));
			out.append(json);
 
			out.flush();
			out.close();
			 
		} catch (IOException e) {
			e.printStackTrace();
		} 
	}
	
	/** Test it 
	 * @throws IOException 
	 * @throws IllegalArgumentException 
	 * @throws FileNotFoundException **/
	public static void main(String [] args) throws FileNotFoundException, IllegalArgumentException, IOException{
		//- Create Settings Object
		Settings obj = new Settings();
			//- Add General Parameters
//			obj.getHadoopGeneralConfiguration().put("fs.defaultFS", "hdfs://83.212.96.14:9000");
//			obj.getHadoopGeneralConfiguration().put("fs.orka.default.config.path", "/usr/local/hadoop/etc/hadoop/");
			
			obj.getHadoopGeneralConfiguration().put("fs.defaultFS", "hdfs://83.212.96.14:9000");
			obj.getHadoopGeneralConfiguration().put("fs.orka.default.config.path", "/usr/local/hadoop/etc/hadoop/");
			
			//- Add Serial Port parameters
			obj.getHadoopUser().put("hadoop.job.ugi", "hduser");
			
			obj.getpithosFSConfiguration().put("fs.pithos.block.size", "4194304");
			obj.getpithosFSConfiguration().put("fs.defaultFS", "hdfs://83.212.96.14:9000");
			obj.getpithosFSConfiguration().put("fs.pithos.impl", "gr.grnet.escience.fs.pithos.PithosFileSystem");
			
			obj.getPithosUser().put("url", "https://pithos.okeanos.grnet.gr/v1");
			obj.getPithosUser().put("username", "fc1bd1b1-9691-4142-b759-12a12a1e6fe3");
			obj.getPithosUser().put("token", "juUVEDtgTftG24r-JA4pAvaU9c-UB2353op42-D0REQ");
		
		//- Generate the json file	
		Configurator.create("hadoopPithosConfiguration.json", obj);
		PithosFileSystem pfs = new PithosFileSystem();
    	pfs.listStatus(new Path("/user"));
	}
	
}