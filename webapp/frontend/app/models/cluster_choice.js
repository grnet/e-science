attr = App.attr;
// Model used for sending user's choices to the backend 
// regarding create cluster information.
App.Clusterchoice = DS.Model.extend({
	project_name : attr('string'),		// name of the project
	cluster_name : attr('string'),		// name of the cluster
	cluster_size : attr('number'),		// size of cluster (master+slaves)
	cpu_master : attr('number'),		// cpus for master
	ram_master : attr('number'),		// ram for master
	disk_master : attr('number'),		// disk for master
	cpu_slaves : attr('number'),		// cpus for slaves
	ram_slaves : attr('number'),		// ram for slaves
	disk_slaves : attr('number'),		// disk for slaves
	disk_template : attr('string'),		// disk template
	os_choice : attr('string'),			// operating system
	ssh_key_selection : attr('string'),	// ssh_key_name
	replication_factor : attr('string'), // hdfs replication factor
	dfs_blocksize : attr('string'),    // hdfs blocksize
	admin_password : attr('string')    // admin_password for hue login
});
