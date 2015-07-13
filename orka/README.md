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
    base_url = < e-science -IP- or -url address- >

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

Optional arguments for all orka commands:
    
    --auth_url="authentication url (default value='https://accounts.okeanos.grnet.gr/identity/v2.0')",
    --token="an ~okeanos token (default value read from ~/.kamakirc)",
    --server_url="orka web application url (default value read from ~/.kamakirc)",

## "images" command

Images command has no required positional or optional arguments.

### {orka images} command example

example for listing available images using defaults from .kamakirc

    orka images 

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
(available images can be found with **orka images** command)
    --replication_factor="HDFS replication factor. Default is 2",
    --dfs_blocksize="HDFS block size (in MB). Default is 128",

### Create Hadoop cluster from a pre-configured image

Using the --image=Hadoop-2.5.2-Debian-8.0 argument creates the Hadoop cluster much faster because it utilises a specially created ~okeanos VM image with Java and YARN pre-installed. Omitting this argument ensures that the latest stable YARN version will be installed (but at the cost of lower speed).

###{orka create} command examples

example for create cluster with default optionals (not hadoop_image):

    orka create Yarn_Test 2 2 2048 10 2 1024 10 Archipelago <project_name>

example for create cluster with a specific image:

    orka create Yarn_Test 2 2 2048 10 2 1024 10 Archipelago <project_name> --image=hadoop_image_name

##"list" command

Optional arguments for list command:

    --status="One of:ACTIVE, PENDING, DESTROYED (case insensitive, shows only clusters of that status)"
    --verbose (outputs full cluster details. Default off)
    
###{orka list} command example

example for list user clusters:

    orka list --status=active --verbose
    
##"info" command

Required positional arguments for info command:

    cluster_id: "Cluster id in e-science database" 
(cluster_id can be found with **orka list** command)

###{orka info} command example

example for cluster info:

    orka info <cluster_id>

##"hadoop" command

Required positional arguments for hadoop command:

    hadoop_status: "START | FORMAT | STOP (case insensitive)"
    cluster_id: "Cluster id in e-science database" 
(cluster_id can be found with **orka list** command)

### {orka hadoop} command examples

example for hadoop start:

    orka hadoop start <cluster_id>

example for hadoop stop:

    orka hadoop stop <cluster_id>

##"destroy" command

Required positional arguments for destroy command:

    cluster_id: "Cluster id in e-science database" 
(cluster_id can be found with **orka list** command)

###{orka destroy} command example

example for destroy cluster:

    orka destroy <cluster_id>

##"file" command

orka file command provides sub-commands for puting files to Hadoop filesystem from local, ftp/http and pithos sources, and getting files from Hadoop filesystem to local and pithos destinations.  
As well a list sub-command for listing pithos files in the URI format expected by orka CLI.

###"file list" command

orka file list is used for returning pithos+ object paths in the format expected by the **source** parameter of **orka file put**.

Optional arguments for file list command:

    --container="a pithos+ container descriptor"
    
####{orka file list} command example

    orka file list --container=/<container_name>
    
###"file get" command

Required positional arguments for file get command:

    cluster_id: "Cluster id in e-science database"
    source: "Hadoop Filesystem object"
    destination: "Local or Pithos+ path"
Pithos destination is differentiated by prepending "pithos://" to the object descriptor

####{orka file get} command examples

    orka file get <cluster_id> <hdfs_file_path> <local_file_path>
    
    orka file get <cluster_id> <hdfs_file_path> pithos://<pithos_file_path>
    
###"file put" command

Required positional arguments for file put command:

    cluster_id: "Cluster id in e-science database"
    source: "Local or ftp/http or pithos+ path"
    destination: "Hadoop Filesystem object"
    
Optional arguments for file put command:

    --user="remote user for ftp/http authentication if required"
    --password="remote user password"

####{orka file put} command examples

example for pithos source:

    orka file put pithos://<pithos_file_path> <hdfs_file_path>
(Properly formatted source can be returned by **orka file list** command)

example for remote server source:

    orka file put <cluster_id> <remote_http_or_ftp_url> <hdfs_file_path>
    
example for local filesystem source:

    orka file put <cluster_id> <local_file_path> <hdfs_file_path>

###"file mkdir" command

Required positional arguments for file mkdir command:

    cluster_id: "Cluster id in e-science database"
    directory: "destination directory on HDFS"
    
Optional arguments for file put command:

    -p (recursive folder creation)

####{orka file mkdir} command examples

example for HDFS folder creation in HDFS home:

    orka file mkdir <cluster_id> <directory>
    
example for recursive HDFS folder creation:

    orka file mkdir -p <cluster_id> <directory_with_non_existant_parent>
    
##"vre create" command

Required positional arguments for vre create command:
        
    name: "name of the VRE server", 
    cpu: "number of CPU cores of VRE server", 
    ram: "ram in MB of VRE server",
    disk: "hard drive in GB of VRE server",
    disk_template: "Standard or Archipelago",
    project_name: "name of a ~okeanos project, to pull resources from"
    
Optional arguments for create vre command:

    --image="Operating System (default value='Debian Base').For vre create this argument must not be left to default"
(available images can be found with **orka images** command)

### {orka vre create} command examples

example for orka vre create with a specific Drupal image:

    orka vre create Drupal_Test 2 2048 20 Standard <project_name>  --image Deb8-Drupal-Final
    
##"vre destroy" command

Required positional arguments for vre destroy command:

    server_id: "VRE Server id in e-science database" 
(server_id is returned after creation of VRE server and will be added later to **orka vre list** command)

### {orka vre destroy} command examples

example for orka vre destroy:

    orka vre destroy <server_id>
    
## Docker Info
Access to a docker container's bash:

    docker exec -t -i container_name bash

Useful links:

    https://www.docker.com/
    https://docs.docker.com/articles/basics/
    https://docs.docker.com/reference/commandline/exec/
    https://github.com/wsargent/docker-cheat-sheet

## Getting help

Also, with

    orka -h
    orka { images | create | vre | destroy | list | info | hadoop | file } -h

helpful information about the orka CLI is depicted and

    orka -V
    orka --version
    
prints current version.