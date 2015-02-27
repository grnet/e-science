// User Welcome controller
App.UserWelcomeController = Ember.Controller.extend({

	needs : 'clusterCreate',
	user_messages : [],
	// flag to see if the transition is from create cluster button
	create_cluster_start : false,
	count : 0,
	sortedclusters : [],
	column : '',
	sortdir : null,
	sortbyname : false,
	sortbydate : false,
	sortbystatus : false,
	sortbyhdpstatus : false,
	sortbysize : false,
	sortbyurl : false,
	ip_of_master : '',
	sortedCollection : function() {
		// sorts content (clusters) based on properties
		return Ember.ArrayProxy.createWithMixins(Ember.SortableMixin, {
			content : this.get('sortedclusters'),
			sortProperties : [this.get('column')],
			sortAscending : this.get('sortdir')
		});
	}.property('sortdir', 'sortbyname', 'sortbydate', 'sortbystatus', 'sortbyhdpstatus', 'sortbysize', 'sortbyurl'),
	master_vm_password_msg : function(){
		var pwd_message = this.get('content.master_vm_password');
		if (!Ember.isBlank(pwd_message)){
			var msg = {'msg_type':'warning','msg_text':pwd_message};
			this.send('addMessage',msg);
		}
	}.observes('content.master_vm_password'),
	actions : {
		// sorts clusters based on selected column (name, date, status, size, IP)
		sortBy : function(clusters, column) {
			// flags used for showing/hiding arrows next to column names
			this.set('sortbynamearrow', false);
			this.set('sortbydatearrow', false);
			this.set('sortbystatusarrow', false);
			this.set('sortbyhdpstatusarrow', false);
			this.set('sortbysizearrow', false);
			this.set('sortbyurlarrow', false);
			this.set('sortedclusters', clusters);
			this.set('column', column);
			switch (column) {
			case 'cluster_name':	
				this.set('sortbynamearrow', true);															
				this.set('sortbyname', !this.get('sortbyname'));
				this.set('sortdir', this.get('sortbyname'));
				break;
			case 'action_date':
				this.set('sortbydatearrow', true);
				this.set('sortbydate', !this.get('sortbydate'));
				this.set('sortdir', this.get('sortbydate'));
				break;
			case 'cluster_status':
				this.set('sortbystatusarrow', true);
				this.set('sortbystatus', !this.get('sortbystatus'));
				this.set('sortdir', this.get('sortbystatus'));
				break;
			case 'hadoop_status':
				this.set('sortbyhdpstatusarrow', true);
				this.set('sortbyhdpstatus', !this.get('sortbyhdpstatus'));
				this.set('sortdir', this.get('sortbyhdpstatus'));
				break;
			case 'cluster_size':
				this.set('sortbysizearrow', true);
				this.set('sortbysize', !this.get('sortbysize'));
				this.set('sortdir', this.get('sortbysize'));
				break;
			case 'master_IP':
				this.set('sortbyurlarrow', true);
				this.set('sortbyurl', !this.get('sortbyurl'));
				this.set('sortdir', this.get('sortbyurl'));
				break;
			}
		},
		addMessage : function(obj){
			// routes/controllers > controller.send('addMessage',{'msg_type':'default|info|success|warning|danger', 'msg_text':'Lorem ipsum dolor sit amet, consectetur adipisicing elit'})
			// templates > {{#each message in user_messages}}message.msg_text{{/each}}
			var store = this.store;
			var messages = store.all('usermessages');
			var arrMessages = messages.toArray();
			var count = messages.get('length') || 0;
			// cap at 10 items for now
			if (count > 9){
				var record = messages.get('firstObject');
				if (!Ember.isEmpty(record)){
					store.deleteRecord(record);
					messages.compact();
				}
			}
			for (i=0;i<count;i++){
				if (arrMessages[i].get('msg_text')==obj['msg_text']){
					return;
				}
			}
			var message = {msg_type: obj['msg_type'], msg_text: obj['msg_text']};
			while (store.hasRecordForId('usermessages',count)){
				count+=1;
			}
			message['id']=count;
			store.createRecord('usermessages', message);
			this.set('user_messages', messages);
		},
		removeMessage : function(id, all){
			// routes/controllers > controller.send('removeMessage', id, [all=false]) optional 3rd parameter to true will clear all messages
			// templates > {{action 'removeMessage' message_id}} / {{action 'removeMessage' 1 true}}
			var store = this.store;
			var messages = store.all('usermessages');
			if (all===true){
				store.unloadAll('usermessages');
			}else{
				var record = store.getById('usermessages', id);
				if (!Ember.isEmpty(record)){
					store.deleteRecord(record);
					messages.compact();
				}
			}
			this.set('user_messages', messages);
		},
		timer : function(status, store) {
			var that = this;
			if (Ember.isNone(this.get('timer'))) {
				this.set('timer', App.Ticker.create({
					seconds : 5,
					onTick : function() {
						that.set('create_cluster_start', false);
						if (!store) {
							store = that.store;
						}
						if (store && that.controllerFor('application').get('loggedIn')) {
							var promise = store.fetch('user', 1);
							promise.then(function(user) {
								// success
								var user_clusters = user.get('clusters');
								var num_records = user_clusters.get('length');
								var bPending = false;
								for ( i = 0; i < num_records; i++) {
									if ((user_clusters.objectAt(i).get('cluster_status') == '2') 
										||(user_clusters.objectAt(i).get('hadoop_status') == '2')) {
										bPending = true;
										var lastsort = that.get('column');
										if (!Ember.isBlank(lastsort)){
											that.send('sortBy', user_clusters, lastsort);
											that.send('sortBy', user_clusters, lastsort);
										}else{
											that.send('sortBy', user_clusters, 'action_date');
											that.send('sortBy', user_clusters, 'action_date');
										}
										break;
									}
								}
								if (!bPending) {
									if (that.get('count') > 0) {
										that.set('count', that.get('count')-1);
									}else{
										that.get('timer').stop();
										status = false;
									}
								}
							}, function(reason) {
								that.get('timer').stop();
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
				}
			}
			if (status) {
				this.get('timer').start();
			} else {
				this.get('timer').stop();
			}
		},
	}
});
