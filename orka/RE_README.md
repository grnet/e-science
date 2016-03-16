# Reproducible Research

Orka supports the re-production of an experiment. The main parameters of an experiment/algorithm/simulation as well as the capabilities of the system that executes this experiment consist the environment of the experiment.
~okeanos facilitates the reproduction of this environment. 

## Description of an experiment

For the reproduction of an experiment, the whole environment should be described, i.e. system capabilities and algorithm. In this manner, the user should define:
    
    cluster information
	configuration settings
	actions

Cluster information consists of:
    
    Name of the cluster to be created
    Size of the Hadoop cluster
    Settings for master and slaves (CPU, Memory, Disk size, Disk template)
    Pre-stored image to be used
	~okeanos project for resources
	Personality file for ssh access

Configuration settings:

	The size of the blocks in HDFS
	The replication factor

If the user desires to re-use an already existing cluster then he needs to state:

    The id of the cluster
    The IP of the master VM

Finally, the user should define the list of actions. The actions that are currently supported are the following:

	- Cluster management
		- Verb: start or stop ot format
		- Arguments: -
		- e.g.  start
				stop
				format
	- Add/Remove nodes
		- Verb: node_add or node_remove
		- Arguments: -
		- e.g. 	node_add
				node_remove
	- Upload/Download files from hdfs
		- Verb: put or get
		- Arguments: source, destination
		- e.g. 	put(source, destination)
				get(source, destination)
	- Run job
		- Verb: run_job
		- Arguments: hadoop user, job
		- e.g. 	run_job(user,job)
		* job should be placed in brackets ""
	- Local command
		- Verb: local_cmd
		- Arguments: the command
		- e.g. 	local_cmd(ls)

YAML files are suitable for the purposes of the Orka Reproducible Research.

## Example 1

In this example, the cluster is created from scratch:

    cluster:
        # cluster to be created
        disk_template: drbd
        flavor_master:
        - 4
        - 4096
        - 20
        flavor_slaves:
        - 4
        - 4096
        - 20
        image: Hadoop-2.5.2
        name: 'test'
        personality: /{{home_dir}}/.ssh/id_rsa.pub
        project_name: escience.grnet.gr
        size: 3
    configuration:
        # configuration settings
        dfs_blocksize: '128'
        replication_factor: '2'
    actions:
        # list of actions
        - local_cmd (ls)
        - node_add
        - put (source,destination(hdfs))
        - run_job (hduser, "/usr/local/hadoop/bin/hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar pi 2 10000")
        - get (source(hdfs),destination)
        - stop
        - format
        - start
        - node_remove
        - local_cmd (ls)
  
## Example 2

Re-use of the same cluster:

    cluster:
        # cluster information
        cluster_id: 1
        master_IP: 12.345.678.90
    actions:
        # list of actions
        - local_cmd (ls)
        - node_add
        - put (source,destination(hdfs))
        - run_job (hduser, "/usr/local/hadoop/bin/hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar pi 2 10000")
        - get (source(hdfs),destination)
        - stop
        - format
        - start
        - node_remove
        - local_cmd (ls)
