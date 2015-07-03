pithosFS Connector for Hadoop
=====

##Overview

The pithosFS Connector plugin for Hadoop, is a plugin for Hadoop that provides the ability to use [pithos+](https://okeanos.grnet.gr/services/pithos/) as an input source and/or output destination.  
The source code is available on [Github](https://github.com/grnet/e-science/tree/develop/pithosfs/java).


##Contents

- [Benefits of using the connector](#benefits-of-using-the-connector)
- [Getting the connector](#getting-the-connector)
- [Configuring the connector](#configuring-the-connector)
- [Manually installing the connector](#manually-installing-the-connector)

##Benefits of using the connector

- **Direct data access**.  
Store your data in pithos+ and access it directly, with no need to transfer it into HDFS first.  
Urls containing pithos:// scheme are automatically handled by the connector.
- **Data accessibility**.  
When you shut down a Hadoop cluster, you still have access to your data in pithos+, unlike HDFS.

##Getting the connector

The pithosFS connector for Hadoop is included as part of the default installation scripts of most e-science clusters and is installed automatically when you create a YARN cluster from the orka application.
If you want to get the connector separately it can be downloaded as a .jar file from [Github](https://github.com/grnet/e-science/tree/develop/pithosfs/java/dist) /dist folder.
To install the connector manually see [manually installing the connector](#manually-installing-the-connector).

##Configuring the connector

When you create a YARN cluster using the orka application, pithosFS connector is automatically configured for use.
There is typically no need to configure the connector further.

To customize the connector, specify configuration values in core-site.xml in the Hadoop configuration directory (typically $HADOOP_HOME/etc/hadoop/) on the cluster on which the connector is installed.

See [manually installing the connector](#manually-installing-the-connector) for configuration details.

##Manually installing the connector

To install the pithosFS connector manually, complete the following steps. 

###Download the connector

See [above](#getting-the-connector).

###Add the connector jar to Hadoop's classpath

Placing the connector in the proper subdirectory of the Hadoop installation is sufficient for the Hadoop class to load it. 
Copy the orka-pithos.jar file to $HADOOP_HOME/share/hadoop/hdfs/lib/ on the cluster machine.
Copy any external libraries needed found at [Github](ttps://github.com/grnet/e-science/tree/develop/pithosfs/java/lib) /lib folder to $HADOOP_HOME/share/hadoop/common/lib/ on the cluster machine.

###Configure Hadoop

The following properties are mandatory to add to the cluster's **core-site.xml**.
```xml
<property>
  <name>auth.pithos.uuid</name>
  <value>abcdefgh-1234-1234-1234-placeholder1</value>
  <description>user Id for ~okeanos</description>
</property>
<property>
  <name>auth.pithos.token</name>
  <value>abCDEfghIGKLmnOpQrSTuVWXyzplaceholder2</value>
 <description>~okeanos access token</description>
</property>
<property>
  <name>fs.pithos.impl</name>
  <value>gr.grnet.escience.fs.pithos.PithosFileSystem</value>
  <description>fqn of class</description>
</property>
<property>
  <name>fs.pithos.url</name>
  <value>https://pithos.okeanos.grnet.gr/v1</value>
  <description>pithos+ REST endpoint</description>
</property>
```
The following property is optional and controls debug output for troubleshooting purposes.
```xml
<property>
  <name>fs.pithos.debug</name>
  <value>false</value>
</property>
```

###Test the installation

On the command line type `hdfs dfs -ls -R -h pithos://<container>/<directory>/` (default container is pithos)
The command should output the directories and objects contained in `<directory>`.
Otherwise see [troubleshooting](#troubleshooting-the-installation).

###Troubleshooting the installation

If the installation test gave the output `No FileSystem for scheme: pithos`, check that you correctly set the mandatory properties in the manual configuration in the correct **core-site.xml**.
If you see the output `java.lang.ClassNotFoundException: gr.grnet.escience.fs.pithos.PithosFileSystem`, then check that you added the connector to Hadoop's classpath. If you see a message about authorization, ensure that you have read-access to `pithos://<container>/<directory>/` and that the credentials in your configuration are correct and/or have not expired.