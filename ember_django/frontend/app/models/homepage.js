attr = App.attr;
// Model for Orka Clusters Statistics 
// Active and Spawned clusters
App.Homepage = DS.Model.extend({
    spawned_clusters : attr('number'),
    active_clusters : attr('number')
});

//Information about images and components
App.Okeanosimage = DS.Model.extend({
	image_name : attr('string'),		// name of the image
	debian : attr('string'),		    // version of debian in the image
	hadoop : attr('string'),		    // version of hadoop in the image
	flume : attr('string'),		    	// version of flume in the image
	oozie : attr('string'),		    	// version of oozie in the image
	spark : attr('string'),		    	// version of spark in the image
	pig : attr('string'),		    	// version of pig in the image
	hive : attr('string'),		   		// version of hive in the image
	hbase : attr('string'),		    	// version of hbase in the image
	hue : attr('string'),		    	// version of hue in the image
	cloudera : attr('string'),			// version of cloudera in the image
});