# Ansible playbooks

The following ansible playbooks are called by run_ansible_playbooks.py python script. Depending on the action executed by the python script, ansible will perform different tasks. The actions of run_ansible_playbooks.py and their corresponding ansible tasks are:

- Hadoop Cluster creation. For this action, ansible configures the Hadoop files, adds a Hadoop user and does whatever configuration is required for the cluster to function correctly. Also, formats the cluster and starts all Hadoop processes, depending on the ~okeanos image used.<br>If the image is a bare Debian Base 8, it also installs every software package required by Hadoop.</br>
- Format Hadoop Cluster. For this action, ansible formats the Hadoop Dsistributed File System, erasing all data  stored there.
- Start Hadoop Cluster. For this action, ansible starts every Hadoop process.
- Stop Hadoop Cluster. For this action, ansible stops every Hadoop process.
- Scale Hadoop Cluster, by adding or removing a node. For this action, ansible does file and user configurations, so the cluster utilize correctly the node(s) added or remain functional if a node is removed.
- Rollback a cluster after failure in scale action. For this action, ansible reverts file configurations to the state they were before the scale cluster failure.

Below are available in tables, the ansible files and folders with their corresponding description:

|    File     | Description
|------------ |:---
|  group_vars/all.yml |  It includes constants and default values for variables used by ansible playbooks.
|  roles      |  It includes the Ansible roles: yarn, cloudera, commons and their corresponding subfolders.
|  site.yml   |  It is the entry point of Ansible and distributes the Ansible tasks based on the input arguments.
|  rollback_scale_cluster.yml    | It is called when the scaling of the cluster fails, so as to rollback the procedure and revert the cluster to the previous functional state.
|  scale_cluster_add_node.yml    | It is called for file and user configurations when adding a node to the Hadoop cluster.
|  scale_cluster_remove_node.yml | It is called for file and user configurations when removing a node from the Hadoop cluster.
|  start_cloudera.yml | It is called so as to start or stop the Cloudera services (Hadoop daemons, Hue, Oozie, Hive, Hbase, Spark) and create mandatory folders in HDFS. <br>Used when role is cloudera.</br>
|  start_yarn.yml     | It is called so as to start or stop Hadoop, Hue and the rest of the Hadoop ecosystem services, depending on the ansible tag used. Also creates mandatory folders in HDFS.<br>Used when role is yarn.</br>
|  ansible.cfg     | Ansible configuration file. Has entries regarding ansible ssh connections.
|  hosts_example   | Example file, serving as a template for the ansible hosts file.

Every Ansible role is in a separate subfolder. In the cases of *yarn* and *cloudera* roles, there are three subfolders, whose description is common and is available below:

|    File     | Description
|------------ |:---
|    files    |  It includes the files that are necessary for the execution of specific services. They are transferred unchanged to the remote machine where commands from the ansible playbooks are executed
|    tasks/main.yml    |  In case of yarn it installs and configures the Apache Hadoop distribution on the cluster. Depending on the ansible tag used, the Hadoop distribution will be Hadoop Base or Hadoop with Hue or Hadoop Ecosystem. <br><br>In case of cloudera it installs and configures, from the cloudera repositories, the cloudera distribution on the cluster.</br></br>
|  templates  |  It includes files with variables, which offers dynamic content. These files are transferred, with the appropriate additions, to the remote machine where commands from the ansible playbooks are executed

In case of *commons* role there is a subfolder whose description is available below:

|    File     | Description
|------------ |:---
|    tasks/main.yml    | Installs sudo and fixes missing locale for every host.