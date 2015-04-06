package org.orka.hadoop.commons;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;

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
	
	/** Test it **/
	public static void main(String [] args){
		//- Create Settings Object
		Settings obj = new Settings();
			//- Hadoop General Parameters
			obj.getHadoopGeneralConfiguration().put("fs.defaultFS", "hdfs://83.212.112.5:9000");
			
			//- Hadoop user
			obj.getHadoopUser().put("hadoop.job.ugi", "hduser");
			
			//- Pithos FS Configuration
			obj.getPithosFSConfiguration().put("fs.defaultFS","pithos://<IP>:<PORT>");
			obj.getPithosFSConfiguration().put("fs.file.impl","org.apache.hadoop.fs.pithos");
			obj.getPithosFSConfiguration().put("fs.pithos.block.size","4194304");
			
			//- Pithos FS Configuration
			obj.getPithosUser().put("url", "https://pithos.okeanos.grnet.gr/v1");
			obj.getPithosUser().put("username", "353ec5f5-8f17-4508-8084-020f78ae82cf");
			obj.getPithosUser().put("token", "ygVkUyRNWsSZo7GM39QtxOAkU5sySmkEHa4arwqY_2U");
		
		//- Generate the json file	
		Configurator.create("hadoopPithosConfiguration.json", obj);
	}
	
}