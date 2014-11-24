Legacy scripts
==============

This directory contains legacy scripts for Hadoop 1.2.x (not supported anymore) and YARN (with older Ansible playbooks)

`create_hadoop_cluster`: creates a Hadoop cluster using threads.

`create_hadoop_cluster_with_ansible`: creates a Hadoop cluster with legacy Ansible playbooks instead of threads.

`run_pi_hadoop and run_wordcount_hadoop`: run pi and wordcount jobs on an existing Hadoop cluster.

`ansible_create_yarn_cluster`: creates a YARN cluster with legacy Ansible playbooks.

`destroy_okeanos_cluster`: destroys a Hadoop cluster.

##How to run cluster creation scripts:

python [script_name.py] [arguments]

    arguments: 
      --name= "name of the cluster" 
      --clustersize= "total VMs, including master node" 
      --cpu_master= "master's node number of cores" 
      --ram_master= "master's node memory in MB",
      --disk_master= "master's node hard drive in GB",
      --cpu_slave= "slave's node number of cores",
      --ram_slave= "slaves's node memory in MB",
      --disk_slave= "slave's node hard drive in GB", 
      --disk_template= "drbd or ext_vlmc" 
      --image= "Operating System (Default Value=Debian Base)", 
      --token= "authentication token", 
      --auth_url= "authentication url (Default Value for okeanos)"
      --logging_level= "6 available logging levels:critical, error, warning, report, info, debug"


####example:

`python script_name.py --name=Yarn_Test --clustersize=4 --cpu_master=2 --ram_master=2048 --disk_master=5 --cpu_slave=2 --ram_slave=1024 --disk_slave=5 --disk_template=ext_vlmc --image='Debian Base' --token=token number --auth_url=https://accounts.okeanos.grnet.gr/identity/v2.0 --logging_level=report`
