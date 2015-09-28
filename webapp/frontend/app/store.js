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

App.UservreserverAdapter = DS.ActiveModelAdapter.extend({
    headers : function() {
        return {
            "Authorization" : App.escience_token,
        };
    }.property("App.escience_token"),
    createRecord: function(store, type, record) {
        var data = this.serialize(record, {
            includeId : true
        });
        var url = 'api/vreservers';
        var headers = this.get('headers');

        return new Ember.RSVP.Promise(function(resolve, reject) {
            jQuery.ajax({
                type : 'POST',
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
    deleteRecord : function(store, type, record) {
        var data = this.serialize(record, {
            includeId : true
        });
        var url = 'api/vreservers';
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
    }
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
    updateRecord : function(store, type, record) {
        var data = this.serialize(record, {
            includeId : true
        });
        var url = 'api/clusterchoices';
        var headers = this.get('headers');

        return new Ember.RSVP.Promise(function(resolve, reject) {
            jQuery.ajax({
                type : 'PUT',
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
    }
});

App.DslAdapter = DS.ActiveModelAdapter.extend({
	headers : function() {
        return {
            "Authorization" : App.escience_token,
        };
    }.property("App.escience_token"),
    createRecord: function(store, type, record) {
        var data = this.serialize(record, {
            includeId : true
        });
        var url = 'api/dsls';
        var headers = this.get('headers');

        return new Ember.RSVP.Promise(function(resolve, reject) {
            jQuery.ajax({
                type : 'POST',
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
    deleteRecord : function(store, type, record) {
        var data = this.serialize(record, {
            includeId : true
        });
        var url = 'api/dsls';
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
    }
});

App.UservreserverSerializer = DS.RESTSerializer.extend({
    attrs : {
        server_IP : {
            key : 'master_IP'
        },
        os_image : {
            key : 'os_choice'
        },
        //server_name : {serialize : false},
        action_date : {serialize : false},
        server_status : {serialize : false},
        //cpu : {serialize : false},
        //ram : {serialize : false},
        //disk : {serialize : false},
        //disk_template : {serialize : false},
        //os_image : {serialize : false},
        //project_name : {serialize : false},
        task_id : {serialize : false},
        state : {serialize : false},
        user : {serialize : false},
        //ssh_key_selection : {serialize : false},
        //admin_password : {serialize : false},
        //admin_email : {serialize : false}
    } 
});

App.DslSerializer = DS.RESTSerializer.extend({
	attrs : {
	    action_date : {serialize : false},
	    task_id : {serialize : false},
        state : {serialize : false},
		user : {serialize : false}
	}
});

App.UserclusterSerializer = DS.RESTSerializer.extend({
    attrs : {
        master_IP : {
            key : 'master_IP'
        },
        cluster_name : {serialize : false},
        action_date : {serialize : false},
        cluster_size : {serialize : false},
        cluster_status : {serialize : false},
        cpu_master : {serialize : false},
        ram_master : {serialize : false},
        disk_master : {serialize : false},
        cpu_slaves : {serialize : false},
        ram_slaves : {serialize : false},
        disk_slaves : {serialize : false},
        disk_template : {serialize : false},
        os_image : {serialize : false},
        project_name : {serialize : false},
        task_id : {serialize : false},
        state : {serialize : false},
        replication_factor : {serialize : false},
        dfs_blocksize : {serialize : false},
        user : {serialize : false}
    }
});

App.UserSerializer = DS.RESTSerializer.extend(DS.EmbeddedRecordsMixin, {
    attrs : {
        clusters : {
            embedded : 'always',
        },
        vreservers : {
            embedded : 'always',
        },
        dsls : {
            embedded : 'always',
        }
    },
});

App.IsodateTransform = DS.Transform.extend({
    deserialize : function(serialized) {
        return Ember.isEmpty(serialized) ? null : moment.utc(serialized, 'YYYY-MM-DD HH:mm:ss').toDate().toISOString();
    },
    serialize : function(deserialized) {
        return Ember.isEmpty(deserialized) ? null : moment.utc(deserialized).format('YYYY-MM-DD HH:mm:ss');
    }
});
App.register('transform:isodate', App.IsodateTransform);

// For fixtures
// App.ApplicationAdapter = DS.FixtureAdapter;