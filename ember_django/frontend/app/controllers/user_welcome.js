// Welcome route controller
// Redirect to logout route when user press logout in welcome screen
App.UserWelcomeController = Ember.Controller.extend({

	needs : 'clusterCreate',
	output_message : '', // output message of create cluster script
	create_cluster_start : false, // flag to see if the transition is from create cluster button

	sortedclusters : [],
	column : '',
	sortdir : null,
	sortbyname : false,
	sortbystatus : false,
	sortbysize : false,
	sortbyurl : false,
	sortedCollection : function() {
		// $options = {
			// title : 'Creating...',
			// fontColor : false,
			// bgColor : 'white',
			// size : 32,
			// isOnly : true,
			// bgOpacity : 0.5,
			// imgUrl : "/frontend/app/images/loading[size].gif",
			// onShow : function() {
				// $.loader.shown = true;
				// $('.loading_wrp').find('span').addClass('text-info');
			// },
			// onClose : function() {
				// $.loader.shown = false;
			// }
		// };
		// $.loader.close(true);
		// setTimeout(function() {
			// $('.glyphicon-time').closest('td').loader($options);
		// }, 100);

		return Ember.ArrayProxy.createWithMixins(Ember.SortableMixin, {
			content : this.get('sortedclusters'),
			sortProperties : [this.get('column')],
			sortAscending : this.get('sortdir')
		});
	}.property('sortdir', 'sortbyname', 'sortbystatus', 'sortbysize', 'sortbyurl'),
	actions : {
		sortBy : function(clusters, column) {
			switch (column) {
			case 'cluster_name':
				this.set('sortbyname', !this.get('sortbyname'));
				this.set('sortdir', this.get('sortbyname'));
				break;
			case 'cluster_status':
				this.set('sortbystatus', !this.get('sortbystatus'));
				this.set('sortdir', this.get('sortbystatus'));
				break;
			case 'cluster_size':
				this.set('sortbysize', !this.get('sortbysize'));
				this.set('sortdir', this.get('sortbysize'));
				break;
			case 'master_IP':
				this.set('sortbyurl', !this.get('sortbyurl'));
				this.set('sortdir', this.get('sortbyurl'));
				break;
			}
			this.set('sortedclusters', clusters);
			this.set('column', column);
		}
	},
});
