Orka
=====


Overview
--------

orka is an interactive command-line tool, and also a
client development library for creating and deleting Hadoop-Yarn clusters of virtual machines
in ~okeanos.

Setup user environment to run orka
--------------------------------
    sudo apt-get update
    sudo apt-get install -y git
    sudo apt-get install -y python python-dev python-pip

 Optional but highly recommended is to install and use the orka package in a virtual environment:
 
    sudo pip install virtualenv
    mkdir .virtualenvs
    cd .virtualenvs
    virtualenv --system-site-packages orkaenv
    . ../.virtualenvs/orkaenv/bin/activate
    (with deactivate from command line you exit the virtual env)
    
Following commands are common for installation in virtual environment or not:

    [sudo if not using virtualenv] pip install ansible==1.7.2
    cd
    git clone <escience git repo> <project_name> [-b develop] (use -b develop if not cloning from grnet/e-science)
    cd to <project_name>/orka-0.1.0
    [sudo if not using virtualenv] python setup.py install
 
  Now orka commands are usable from anywhere .





For testing in a minimum Debian Base virtual machine in ~okeanos:
---------------------------------------------------------------------------
Following commands must be executed before anything else:
    
    apt-get update
    apt-get install sudo
    adduser newuser
    adduser newuser sudo
    su - newuser
    ssh-keygen

How to run orka commands
------------------------
orka -h [command] -h "arguments"

arguments for create command:
     
      --name="name of the cluster" 
      --cluster_size="total VMs,including master node" 
      --cpu_master="master's node number of cores" 
      --ram_master= "master's node memory in MB",
      --disk_master= "master's node hard drive in GB",
      --cpu_slave= "slave's node number of cores",
      --ram_slave= "slaves's node memory in MB",
      --disk_slave= "slave's node hard drive in GB", 
      --disk_template= "drbd or ext_vlmc" 
      --image="operating System (Default Value Debian Base)", 
      --token="an ~okeanos token", 
      --auth_url="authentication url (Default Value)"
      --logging="7 logging levels:critical, error, warning, summary, report, info, debug (Default Value summary)"
      --project_name="name of a ~okeanos project"

example for create cluster:

    orka create --name=Yarn_Test --cluster_size=3 --cpu_master=4 --ram_master=2048 --disk_master=5 --cpu_slave=2 --ram_slave=1024 --disk_slave=5 --disk_template=ext_vlmc --image='Debian Base' --token=an_~okeanos_token --auth_url=https://accounts.okeanos.grnet.gr/identity/v2.0 --logging=report --project_name=~okeanos_project_name

arguments for destroy command :

    --master_ip="Public ip of the master vm of the Hadoop cluster"
    --token="an ~okeanos token"
    --logging="7 logging levels:critical, error, warning, summary, report, info, debug (Default Value summary)"

example for destroy cluster:

    orka destroy --master_ip=83.83.83.83 --token=an_~okeanos_token

Also, with

    orka -h
    orka create -h
    orka destroy -h
helpful text about the orka CLI is depicted.

Miscellaneous info
----------------
- After cluster creation, the root password of the master virtual machine will be inside a file named [master_vm name]_root_password in the current working directory.
- In the config.txt file of the project is the public ip of the nginx server in ~okeanos.It is required for updating the orka database.
- For the time being, a user who wants to create a cluster with orka must have a public ssh key in ~/.ssh/ .It can be created with ssh-keygen command.