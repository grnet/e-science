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
    cd to <project_name>/orka-0.1.1
    [sudo if not using virtualenv] python setup.py install
 
  Now orka commands are usable from anywhere .





######If no public ssh key exists in default directory (~/.ssh/), the user, before running orka, must create a key with:

    ssh-keygen -f id_rsa -t rsa -N ''
    


How to run orka commands
------------------------
orka [command] "arguments"

Required positional arguments for create command:
         
    name="name of the cluster" 
    cluster_size="total VMs, including master node" 
    cpu_master="master node: number of CPU cores" 
    ram_master="master node: memory in MB",
    disk_master="master node: hard drive in GB",
    cpu_slave="each slave node: number of CPU cores",
    ram_slave="each slave node: memory in MB",
    disk_slave="each slave node: hard drive in GB",
    disk_template= "Standard or Archipelago"
    token="an ~okeanos token",
    project_name="name of a ~okeanos project, to pull resources from"
    
Optional arguments for create command:

    --image="Operating System (Default Value=Debian Base)",
    --auth_url="authentication url (Default Value=https://accounts.okeanos.grnet.gr/identity/v2.0)"
    --logging="critical, error, warning, summary, report, info, debug (Default Value=summary)"
    --use_hadoop_image="name of a hadoop image. Overrides image value" (Default value=HadoopImage)

Install from a pre-configured image
----------------------------------

    Using the --use_hadoop_image argument creates the Hadoop cluster much faster because it utilises a specially
    created ~okeanos VM image with Java and YARN pre-installed. Omitting this argument ensures that the latest
    stable YARN version will be installed (but at the cost of lower speed).

example for create cluster with default optionals (not hadoop_image):

    orka create Yarn_Test 2 2 2048 10 2 1024 10 Archipelago <~okeanos_token> <project_name>

example for create cluster with default optionals (with default hadoop image):

    orka create Yarn_Test 2 2 2048 10 2 1024 10 Archipelago <~okeanos_token> <project_name> --use_hadoop_image

example for create cluster with a different hadoop image and logging level:

    orka create Yarn_Test 2 2 2048 10 2 1024 10 Archipelago <~okeanos_token> <project_name> --use_hadoop_image=hadoop_image_name --logging=report

Required positional arguments for destroy command :

    master_ip="Public ip of the master VM of the Hadoop cluster"
    token="an ~okeanos token"

Optional arguments for destroy command:

    --logging="7 logging levels:critical, error, warning, summary, report, info, debug (Default Value summary)"

example for destroy cluster:

    orka destroy 83.83.83.83 <~okeanos_token> --logging=report

Required positional arguments for list command :

    token="an ~okeanos token"

Optional arguments for list command:

    --status="3 cluster status:ACTIVE, PENDING, DESTROYED (case insensitive,shows only clusters of that status)"
    --verbose (outputs full cluster details. Default off)

example for list user clusters:

    orka list <~okeanos_token> --status=active --verbose

Also, with

    orka -h
    orka create -h
    orka destroy -h
    orka list -h

helpful information about the orka CLI is depicted and

    orka -V
    orka --version

prints current version.

Miscellaneous info
----------------
- After cluster creation, the root password of the master virtual machine will be inside a file named [master_vm name]_root_password in the current working directory.
- In the config.txt file of the project is the public ip of the nginx server in ~okeanos.It is required for updating the orka database.
