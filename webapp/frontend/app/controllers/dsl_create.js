safestr = Ember.Handlebars.SafeString;
// escience reproducible experiments DSL Create controller
App.DslCreateController = Ember.Controller.extend({
    needs : ['userWelcome'],
    
    // NYI
    experiment_yaml_static : null,
    experiment_yaml : function(key, value){
        if (arguments.length > 1){//setter
            var formatted = new safestr(value);
            this.set('experiment_yaml_static',formatted);
        }
        return Ember.isEmpty(this.get('experiment_yaml_static')) ? '' : this.get('experiment_yaml_static');//getter
    }.property('experiment_yaml_static'),
       
    dsl_filename_static : null,
    dsl_filename : function(key, value) {
        if (arguments.length > 1) {//setter
            this.set('dsl_filename_static', value);
        }
        return Ember.isEmpty(this.get('dsl_filename_static')) ? '' : this.get('dsl_filename_static');//getter
    }.property('dsl_filename_static'),
    dsl_pithos_path_static : null,
    dsl_pithos_path : function(key, value) {
        if (arguments.length > 1) {//setter
            this.set('dsl_pithos_path_static', value);
        }
        return Ember.isEmpty(this.get('dsl_pithos_path_static')) ? '' : this.get('dsl_pithos_path_static');//getter
    }.property('dsl_pithos_path_static'),
    
    // userclusters block
    filtered_clusters : function(){
        var filter_by = this.get('cluster_active_filter') && ['ACTIVE'] || ['DESTROYED','ACTIVE'];
        return Ember.isEmpty(this.get('user_clusters')) ? [] : this.get('user_clusters').filter(function(item, index, original) {
            return filter_by.contains(item.get('cluster_status_verbose'));
        });
    }.property('user_clusters.[]','user_clusters.isLoaded','cluster_active_filter'),
    
    boolean_no_cluster : true,
    cluster_select_observer : function(){
        if (Ember.isEmpty(this.get('selected_cluster_id'))){
            this.set('boolean_no_cluster',true);
            this.set('selected_cluster',null);
        }else{
            var selected_cluster = this.get('filtered_clusters').filterBy('id',this.get('selected_cluster_id'));
            if (Ember.isEmpty(selected_cluster)) this.set('selected_cluster_id',null);
            this.set('selected_cluster',selected_cluster);
            this.set('boolean_no_cluster',false);
            this.set('alert_missing_input_dsl_source',null);
        }
    }.observes('selected_cluster_id','filtered_clusters'),
    selectec_cluster_size : function(){
        return Ember.isEmpty(this.get('selected_cluster')) ? '' : this.get('selected_cluster').objectAt(0).get('cluster_size');
    }.property('selected_cluster'),
    selected_cluster_master_flavor : function(){
        var cluster = Ember.isEmpty(this.get('selected_cluster')) ? null : this.get('selected_cluster').objectAt(0);
        return cluster && '[CPUx%@, RAM:%@MiB, DISK:%@GiB]'.fmt(cluster.get('cpu_master'),cluster.get('ram_master'),cluster.get('disk_master')) || '';
    }.property('selected_cluster'),
    selected_cluster_slaves_flavor : function(){
        var cluster = Ember.isEmpty(this.get('selected_cluster')) ? null : this.get('selected_cluster').objectAt(0);
        return cluster && '[CPUx%@, RAM:%@MiB, DISK:%@GiB]'.fmt(cluster.get('cpu_slaves'),cluster.get('ram_slaves'),cluster.get('disk_slaves')) || '';
    }.property('selected_cluster'),
    selected_cluster_project : function(){
        return Ember.isEmpty(this.get('selected_cluster')) ? '' : this.get('selected_cluster').objectAt(0).get('project_name');
    }.property('selected_cluster'),
    
    //utility functions
    alert_input_missing_boundto : {
        // data column > alert message property, input control element id
        cluster_id : ['alert_missing_input_dsl_source','#id_dsl_cluster'],
        dsl_name : ['alert_missing_input_dsl_name','#id_dsl_filename'],
        pithos_path : ['alert_missing_input_pithos_path','#id_pithos_destination'],
    },
    alert_input_missing_text : {
        // alert message property > message text
        alert_missing_input_dsl_source : 'Please select a cluster to save config metadata from',
        alert_missing_input_dsl_name : 'Please type in or generate default metadata filename',
        alert_missing_input_pithos_path : 'Please type in or generate default pithos container/path',
    },
    missing_input : function(that, new_dsl){
        var self = that; // get the controller reference into self
        // clear alerts on new check
        for (alert in self.get('alert_input_missing_text')){
            self.set(alert,null);
        }
        for (property in new_dsl) {
            if (Ember.isEmpty(new_dsl[property])) {
                var alert_prop_name = self.get('alert_input_missing_boundto')[property][0];
                self.set(alert_prop_name,self.get('alert_input_missing_text')[alert_prop_name]);
                var input_element = $(self.get('alert_input_missing_boundto')[property][1]);
                window.scrollTo(input_element.offsetLeft, input_element.offsetTop);
                input_element.focus();
                return true;
            }
        }
        return false;
    },
    
    actions : {
        dsl_create : function() {
            var self = this;
            var store = this.get('store');
            var model = this.get('content');
            var cluster_id = this.get('selected_cluster_id');
            var dsl_name = this.get('dsl_filename');
            var pithos_path = this.get('dsl_pithos_path');
            var new_dsl = {
                'cluster_id' : cluster_id,
                'dsl_name' : dsl_name,
                'pithos_path' : pithos_path
            }; 
            if (this.get('missing_input')(self, new_dsl)){
                return;
            }
            // unload cached records
            store.unloadAll('dsl');
            store.fetch('user', 1).then(function(user) {
                //success
                var new_record = store.createRecord('dsl', new_dsl);
                new_record.save().then(function(data) {
                    var msg = {
                        'msg_type' : 'success',
                        'msg_text' : 'Metadata saved as \"%@\" in %@'.fmt(dsl_name,pithos_path)
                    };
                    self.get('controllers.userWelcome').send('addMessage', msg);
                    self.set('controllers.userWelcome.create_cluster_start', true);
                    self.get('controllers.userWelcome').send('setActiveTab','dsls');
                    Ember.run.next(function(){self.transitionToRoute('user.welcome');});
                }, function(reason) {
                    var msg = {
                        'msg_type' : 'danger',
                        'msg_text' : 'Failed to create file \"%@\" in %@ with error: %@'.fmt(dsl_name,pithos_path,reason.message)
                    };
                    self.get('controllers.userWelcome').send('addMessage', msg);
                });
            }, function(reason) {
                //error
                console.log(reason.message);
            });
        },
        dsl_filename_default : function() {
            var model = this.get('content');
            var store = this.get('store');
            var date_now = new safestr(moment(Date.now()).format('YYYY-MM-DD_HH-mm-ss'))['string'];
            var cluster_id = null;
            var cluster_name = null;
            if (!Ember.isEmpty(this.get('selected_cluster'))){
                cluster_id = this.get('selected_cluster_id');
                cluster_name = this.get('selected_cluster').objectAt(0).get('cluster_name_noprefix') || '';
            }
            if (Ember.isEmpty(cluster_id) || Ember.isEmpty(cluster_name)){
                this.set('alert_missing_input_dsl_source',this.get('alert_input_missing_text')['alert_missing_input_dsl_source']);
                return;
            }
            var default_filename = "%@_%@_%@-%@".fmt(cluster_name, cluster_id, date_now, 'cluster-metadata');
            this.set('dsl_filename', default_filename);
        },
        dsl_pithospath_default : function() {
            this.set('dsl_pithos_path', 'pithos');
        },
        set_selected_cluster : function(cluster_id){
            var clusterid = cluster_id || this.get('cluster_id') || 0;
            Ember.isEmpty(this.get('selected_cluster_id')) ? this.set('selected_cluster_id',cluster_id) : this.set('selected_cluster_id',this.get('selected_cluster_id'));
        },
        reset : function(){
            var self = this;
            this.set('dsl_filename','');
            this.set('dsl_pithos_path','');
            this.set('selected_cluster_id',null);
            this.set('cluster_active_filter',null);
            for (alert in self.get('alert_input_missing_text')){
                self.set(alert,null);
            }
        }
    }
});
