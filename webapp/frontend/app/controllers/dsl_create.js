// escience reproducible research DSL Create controller
App.DslCreateController = Ember.Controller.extend({
    needs : ['userWelcome'],
    file_count : 0,
    cluster_id : 0,
    cluster_name : '',
    // data-bound to template
    dsl_filename_static : null,
    dsl_filename : function(key, value) {
        if (arguments.length > 1) {//setter
            this.set('dsl_filename_static', value);
        }
        return Ember.isEmpty(this.get('dsl_filename_static')) ? '' : this.get('dsl_filename_static');
        //getter
    }.property('dsl_filename_static'),
    dsl_pithos_path_static : null,
    dsl_pithos_path : function(key, value) {
        if (arguments.length > 1) {//setter
            this.set('dsl_pithos_path_static', value);
        }
        return Ember.isEmpty(this.get('dsl_pithos_path_static')) ? '' : this.get('dsl_pithos_path_static');
        //getter
    }.property('dsl_pithos_path_static'),

    actions : {
        dsl_create : function() {
            var self = this;
            var store = this.get('store');
            var model = this.get('content');
            var cluster_id = this.get('cluster_id');
            var dsl_name = this.get('dsl_filename');
            var pithos_path = this.get('dsl_pithos_path');
            // unload cached records
            store.unloadAll('dsl');
            store.fetch('user', 1).then(function(user) {
                //success
                var response = store.createRecord('dsl', {
                    'id' : 1,
                    'dsl_name' : dsl_name,
                    'pithos_path' : pithos_path,
                    'cluster_id' : cluster_id,
                }).save();
                response.then(function(data) {
                    var msg = {
                        'msg_type' : 'success',
                        'msg_text' : 'File(%@) with cluster metadata has transferred to pithos container'.fmt(self.get('file_count'))
                    };
                    self.get('controllers.userWelcome').send('addMessage', msg);
                }, function(reason) {
                    var msg = {
                        'msg_type' : 'danger',
                        'msg_text' : 'Failed to transfer file(%@) with cluster metadata to pithos container'.fmt(self.get('file_count'))
                    };
                    self.get('controllers.userWelcome').send('addMessage', msg);
                });
                self.set('file_count', self.get('file_count') + 1);
                self.get('controllers.userWelcome').send('setActiveTab', 'dsls');
                // TODO: reset action
                self.set('dsl_filename','');
                self.set('dsl_pithos_path','');
                self.transitionToRoute('user.welcome');
            }, function(reason) {
                //error
                console.log(reason);
            });
        },
        dsl_filename_default : function() {
            var model = this.get('content');
            var store = this.get('store');
            var date_now = new safestr(moment(Date.now()).format('YYYY-MM-DD_HH-mm-ss'))['string'];
            var default_filename = "%@_%@_%@-%@".fmt(this.get('cluster_name'), this.get('cluster_id'), date_now, 'cluster-metadata');
            this.set('dsl_filename', default_filename);
        },
        dsl_pithospath_default : function() {
            this.set('dsl_pithos_path', 'pithos');
        },
    }
});
