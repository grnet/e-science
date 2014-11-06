// Model used for sending user's choices regarding create cluster information
Orka.Clusterchoice = DS.Model.extend({
	cluster_name : DS.attr('string'),
	cluster_size : DS.attr('number'),
	cpu_master : DS.attr('number'),
	mem_master : DS.attr('number'),
	disk_master : DS.attr('number'),
	cpu_slaves : DS.attr('number'),
	mem_slaves : DS.attr('number'),
	disk_slaves : DS.attr('number'),
	disk_template : DS.attr('string'),
	os_choice : DS.attr('string')

});
