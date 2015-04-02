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
			//- Add General Parameters
			obj.getHadoopGeneralConfiguration().put("fs.defaultFS", "hdfs://83.212.112.5:9000");
			obj.getHadoopGeneralConfiguration().put("fs.orka.default.config.path", "/usr/local/hadoop/etc/hadoop/");
			
			//- Add Serial Port parameters
			obj.getHadoopUser().put("hadoop.job.ugi", "hduser");
			
		
		//- Generate the json file	
		Configurator.create("hadoopPithosConfiguration.json", obj);
	}
	
}