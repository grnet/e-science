package tests;

import gr.grnet.escience.fs.pithos.PithosFileSystem;

import java.security.PrivilegedExceptionAction;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.security.UserGroupInformation;

public class KouKou {

    public static void main(String args[]) {

        try {
            UserGroupInformation ugi
                = UserGroupInformation.createRemoteUser("hduser");

            ugi.doAs(new PrivilegedExceptionAction<Void>() {

                public Void run() throws Exception {
                	
                	PithosFileSystem pfs = new PithosFileSystem();
                	pfs.listStatus(new Path("/user"));

//                    Configuration conf = new Configuration();
////                     conf.set("fs.defaultFS", "hdfs://83.212.96.14:9000");
////                     conf.set("fs.default.name", "pithos://83.212.96.14");
//                     conf.set("fs.defaultFS", "pithos://83.212.96.14:9000");
//                     conf.set("fs.pithos.impl", "grnet.escience.fs.pithos.PithosFileSystem");                  
//                     conf.set("hadoop.job.ugi", "hduser");
//
//                    FileSystem fs = FileSystem.get(conf);
//
//                    //fs.createNewFile(new Path("/user/hduser/kostest.txt"));
//
//                    FileStatus[] status = fs.listStatus(new Path("/user"));
//                    for(int i=0;i<status.length;i++){
//                        System.out.println(status[i].getPath());
//                    }
                    return null;
                }
            });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
