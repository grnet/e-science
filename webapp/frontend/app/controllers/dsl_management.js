App.DslManagementController = Ember.Controller.extend({
	
    needs : ['application', 'dslCreate', 'userWelcome'],
    count : 0,   
    
    initial_timer_active : function(){
        return this.get('count')>0;
    }.property('count'),
    user_theme_changed : function(){
        var new_theme = this.get('controllers.application').get('user_theme');
        this.set('user_theme',new_theme);
    }.observes('controllers.application.user_theme'),
    actions_dsl_disabled : function(){
        return this.get('content.dsl_status') == "1" || this.get('initial_timer_active');
    }.property('content.dsl_status','initial_timer_active'),
    
    actions : {
        timer : function(status, store) {
            var that = this;
            if (Ember.isNone(this.get('timer'))) {
                this.set('timer', App.Ticker.create({
                    seconds : 5,
                    onTick : function() {
                        if (!store) {
                            store = that.store;
                        }
                        if (store && that.get('controllers.application').get('loggedIn')) {
                            var promise = store.fetch('user', 1);
                            promise.then(function(user) {
                                // success
                                var user_dsls = user.get('dsls');
                                var num_records = user_dsls.get('length');
                                var model = that.get('content');
                                var dsl_id = model.get('id');
                                var bPending = false;
                                for ( i = 0; i < num_records; i++) {
                                    if ((user_dsls.objectAt(i).get('id') == dsl_id) 
                                    && ((user_dsls.objectAt(i).get('dsl_status') == '1'))) {
                                        bPending = true;
                                        break;
                                    }
                                }
                                if (!bPending) {
                                    if (that.get('count') > 0) {
                                        that.set('count', that.get('count') - 1);
                                    } else {
                                        that.get('timer').stop();
                                        that.set('count', 0);
                                        status = false;
                                    }
                                }
                            }, function(reason) {
                                that.get('timer').stop();
                                that.set('count', 0);
                                status = false;
                                console.log(reason.message);
                            });
                            return promise;
                        }
                    }
                }));
            } else {
                if (status) {
                    that.get('timer').start();
                } else {
                    that.get('timer').stop();
                    that.set('count', 0);
                }
            }
            if (status) {
                this.get('timer').start();
            } else {
                this.get('timer').stop();
                that.set('count', 0);
            }
        },        
    }
});