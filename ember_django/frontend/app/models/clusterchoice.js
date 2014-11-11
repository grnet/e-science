attr = App.attr;
// Model used for sending user's choices regarding create cluster information
App.Clusterchoice = DS.Model.extend({
	cluster_name : attr('string'),
	cluster_size : attr('number'),
	cpu_master : attr('number'),
	mem_master : attr('number'),
	disk_master : attr('number'),
	cpu_slaves : attr('number'),
	mem_slaves : attr('number'),
	disk_slaves : attr('number'),
	disk_template : attr('string'),
	os_choice : attr('string')
});