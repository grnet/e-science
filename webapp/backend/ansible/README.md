# Ansible playbooks

Below are available in tables, the ansible files and folders with their corresponding description:

|    File     | Description
|------------ |:---
|  group_vars/all.yml |  It includes constants and default values for variables used by ansible playbooks.
|  roles      |  It includes the Ansible roles: yarn, cloudera, commons and their corresponding subfolders.
|  site.yml   |  It is the entry point of Ansible and distributes the Ansible tasks based on the input arguments.
|  rollback_scale_cluster    | It is called when the scaling of the cluster fails, so as to rollback the procedure and revert the cluster to the previous functional state.
|  scale_cluster_add_node    | It is called for file and user configurations when adding a node to the Hadoop cluster.
|  scale_cluster_remove_node | It is called for file and user configurations when removing a node from the Hadoop cluster.
|  start_cloudera | It is called so as to start or stop the Cloudera services (Hadoop daemons, Hue, Oozie, Hive, Hbase, Spark) and create mandatory folders in HDFS. Used when role is cloudera.
|  start_yarn     | It is called so as to start or stop Hadoop, Hue and the rest of the Hadoop ecosystem services, depending on the ansible tag used. Also creates mandatory folders in HDFS. Used when role is yarn.
|  ansible.cfg     | Ansible configuration file. Has entries regarding ansible ssh connections.
|  hosts_example   | Example file, serving as a template for the ansible hosts file.

Every Ansible role is in a separate subfolder. In the cases of *yarn* and *cloudera* roles, there are three subfolders, whose description is common and is available below:

|    File     | Description
|------------ |:---
|    files    |  It includes the files that are necessary for the execution of specific services. They are transferred unchanged to the remote machine where commands from the ansible playbooks are executed
|    tasks    |  In case of yarn it installs and configures the Apache Hadoop distribution on the cluster. Depending on the ansible tag used, the Hadoop distribution will be Hadoop Base or Hadoop with Hue or Hadoop Ecosystem. In case of cloudera it installs and configures, from the cloudera repositories, the cloudera distribution on the cluster.  
|  templates  |  It includes files with variables, which offers dynamic content. These files are transferred, with the appropriate additions, to the remote machine where commands from the ansible playbooks are executed

In case of *commons* role there is a subfolder whose description is available below:

|    File     | Description
|------------ |:---
|    tasks    | Installs sudo and fixes missing locale for every host.