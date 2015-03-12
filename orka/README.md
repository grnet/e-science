Orka
=====

###Overview

orka is a command-line tool, and also a client development library, for creating and deleting Hadoop (YARN) clusters of virtual machines in ~okeanos IaaS.

##Setup user environment to run orka (Debian)

    sudo apt-get update
    sudo apt-get install -y git
    sudo apt-get install -y python python-dev python-pip

##Adding [orka]      section to kamaki config file

User should open ~/.kamakirc and append these two lines:
    
    [orka]                                                              
    base_url = **< e-science -IP- or -url address- >**

###Virtual environment

Optional but highly recommended is to install and use the orka package in a virtual environment:
 
    sudo pip install virtualenv
    mkdir .virtualenvs
    cd .virtualenvs
    virtualenv --system-site-packages orkaenv
    . ../.virtualenvs/orkaenv/bin/activate
    (with deactivate from command line you exit the virtual env)
    
Following commands download and install orka (either directly or in virtual environment):

    [sudo if not using virtualenv] pip install ansible==1.7.2
    cd
    git clone <escience git repo> <project_name> 
    cd to <project_name>/orka
    [sudo if not using virtualenv] python setup.py install
 
  Now orka commands are usable from anywhere.

##How to run orka commands

$ orka [command] "arguments"

## "create" command

Required positional arguments for create command:
         
    name: "name of the cluster" 
    cluster_size: "total VMs, including master node" 
    cpu_master: "master node: number of CPU cores" 
    ram_master: "master node: ram in MB",
    disk_master: "master node: hard drive in GB",
    cpu_slave: "each slave node: number of CPU cores",
    ram_slave: "each slave node: ram in MB",
    disk_slave: "each slave node: hard drive in GB",
    disk_template: "Standard or Archipelago"
    project_name: "name of a ~okeanos project, to pull resources from"
    
Optional arguments for create command:

    --image="Operating System (default value='Debian Base')",
    --auth_url="authentication url (default value='https://accounts.okeanos.grnet.gr/identity/v2.0')",
    --token="an ~okeanos token (default value read from ~/.kamakirc)",
    --use_hadoop_image="name of a Hadoop image. Overrides image value (default value='HadoopImage')"

### Create Hadoop cluster from a pre-configured image

Using the --use_hadoop_image argument creates the Hadoop cluster much faster because it utilises a specially created ~okeanos VM image with Java and YARN pre-installed. Omitting this argument ensures that the latest stable YARN version will be installed (but at the cost of lower speed).

###{orka create} command examples

example for create cluster with default optionals (not hadoop_image):

    orka create Yarn_Test 2 2 2048 10 2 1024 10 Archipelago <project_name>

example for create cluster with default optionals (with default hadoop image):

    orka create Yarn_Test 2 2 2048 10 2 1024 10 Archipelago <project_name> --use_hadoop_image

example for create cluster with a different hadoop image:

    orka create Yarn_Test 2 2 2048 10 2 1024 10 Archipelago <project_name> --use_hadoop_image=hadoop_image_name

##"list" command

Optional arguments for list command:

    --status="One of:ACTIVE, PENDING, DESTROYED (case insensitive, shows only clusters of that status)"
    --token="an ~okeanos token (Default Value read from ~/.kamakirc)",
    --verbose (outputs full cluster details. Default off)
    
###{orka list} command example

example for list user clusters:

    orka list --status=active --verbose
    
##"info" command

Required positional arguments for info command:

    cluster_id: "Cluster id in e-science database" 
(cluster_id can be found with **orka list** command)

Optional arguments for info command:

    --token="an ~okeanos token (default value read from ~/.kamakirc)",

###{orka info} command example

example for cluster info:

    orka info <cluster_id>

##"hadoop" command

Required positional arguments for hadoop command:

    hadoop_status: "START | FORMAT | STOP (case insensitive)"
    cluster_id: "Cluster id in e-science database" 
(cluster_id can be found with **orka list** command)

Optional arguments for hadoop command:

    --token="an ~okeanos token (default value read from ~/.kamakirc)",

### {orka hadoop} command examples

example for hadoop start:

    orka hadoop start <cluster_id>

example for hadoop stop:

    orka hadoop stop <cluster_id>

##"destroy" command

Required positional arguments for destroy command:

    cluster_id: "Cluster id in e-science database" 
(cluster_id can be found with **orka list** command)

Optional arguments for destroy command:

    --token="an ~okeanos token (default value read from ~/.kamakirc)",

###{orka destroy} command example

example for destroy cluster:

    orka destroy <cluster_id>


## Getting help

Also, with

    orka -h
    orka { create | destroy | list | info | hadoop } -h

helpful information about the orka CLI is depicted and

    orka -V
    orka --version
    
prints current version.