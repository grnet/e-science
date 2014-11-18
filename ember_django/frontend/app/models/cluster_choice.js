attr = App.attr;
// Model used for sending user's choices regarding create cluster information
App.Clusterchoice = DS.Model.extend({
	cluster_name : attr('string'),		// name of the cluster
	cluster_size : attr('number'),		// size of cluster (master+slaves)
	cpu_master : attr('number'),		// cpus for master
	mem_master : attr('number'),		// memory for master
	disk_master : attr('number'),		// disk for master
	cpu_slaves : attr('number'),		// cpus for slaves
	mem_slaves : attr('number'),		// memory for slaves
	disk_slaves : attr('number'),		// disk for slaves
	disk_template : attr('string'),		// disk template
	os_choice : attr('string')		// operating system
});