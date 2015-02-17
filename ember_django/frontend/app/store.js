/* 
 The store holds locally data loaded from the server (i.e. records). 
 Routes and controllers can query the store for records. 
 If a given record is called for the first time, then the store tells the adapter to load it over the network. 
 Then, the store caches it for the next time you ask for it. 
*/

// Extend Application Adapter settings for Token Authentication and REST calls to /api
// Changes of global var escience_token are reflected in the Authorization header of our REST calls
App.ApplicationAdapter = DS.ActiveModelAdapter.extend({
	namespace : 'api',
	headers : function() {
		return {
			"Authorization" : App.escience_token
		};
	}.property("App.escience_token"),
});

App.UserclusterAdapter = DS.ActiveModelAdapter.extend({
	headers : function() {
		return {
			"Authorization" : App.escience_token,
		};
	}.property("App.escience_token"),
	deleteRecord : function(store, type, record) {
		var data = this.serialize(record, {
			includeId : true
		});

		var url = 'api/clusterchoices';
		var headers = this.get('headers');

		return new Ember.RSVP.Promise(function(resolve, reject) {
			jQuery.ajax({
				type : 'DELETE',
				headers : headers,
				url : url,
				dataType : 'json',
				data : data
			}).then(function(data) {
				Ember.run(null, resolve, data);
			}, function(jqXHR) {
				jqXHR.then = null;
				// tame jQuery's ill mannered promises
				Ember.run(null, reject, jqXHR);
			});
		});
	},
});

App.UserclusterSerializer = DS.RESTSerializer.extend({
	attrs : {
		master_IP : {key : 'master_IP'},
		cluster_name : {serialize: false},
		action_date : {serialize: false},
		cluster_size : {serialize: false},
		cluster_status : {serialize: false},
		cpu_master : {serialize: false},
		mem_master : {serialize: false},
		disk_master : {serialize: false},
		cpu_slaves : {serialize: false},
		mem_slaves : {serialize: false},
		disk_slaves : {serialize: false},
		disk_template : {serialize: false},
		os_image : {serialize: false},
		project_name : {serialize: false},
		task_id : {serialize: false},
		state : {serialize: false},
		// hadoop_status : {serialize: false},
		user : {serialize: false},
	},
});

App.UserSerializer = DS.RESTSerializer.extend(DS.EmbeddedRecordsMixin, {
	attrs : {
		clusters : {
			embedded : 'always',
		}
	},
});

App.IsodateTransform = DS.Transform.extend({  
  deserialize: function(serialized) {
    return Ember.isEmpty(serialized) ? null : moment.utc(serialized, 'YYYY-MM-DD HH:mm:ss').toDate().toISOString();
  },
  serialize: function(deserialized) {
    return Ember.isEmpty(deserialized) ? null : moment.utc(deserialized).format('YYYY-MM-DD HH:mm:ss');
  }
});
App.register('transform:isodate', App.IsodateTransform);

// For fixtures
// App.ApplicationAdapter = DS.FixtureAdapter;