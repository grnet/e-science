App.Ticker = Ember.Object.extend({
	seconds : 0,
	minutes : 0,
	ticking : false,
	interval : function() {
		return (this.get('minutes') * 60 + this.get('seconds')) * 1000 || 5000;
		// Time between ticks (in miliseconds)
	}.property(),
	// Schedules the function `f` to be executed every `interval` time.
	schedule : function(f) {
		return Ember.run.later(this, function() {
			f.apply(this);
			this.set('timer', this.schedule(f));
		}, this.get('interval'));
	},
	// Stops the timer
	stop : function() {
		if (this.get('ticking')){
			Ember.run.cancel(this.get('timer'));
			this.set('ticking', false);
		}
	},
	// Starts the timer, i.e. executes the `onTick` function every interval.
	start : function() {
		if (!this.get('ticking')){
			var func = this.get('onTick');
			Ember.run.once(this, function(){
				func.apply(this);
			});
			this.set('timer', this.schedule(func));
			this.set('ticking', true);
		}
	},
	// overriden with the function we want to execute where the Timer object is instantiated
	// example: var ticker = App.Ticker.create({seconds: 3, onTick: function(){console.log('tock!');}});
	// ticker.reopen({seconds: 5, onTick: function(){console.log('ding');}});
	onTick : function() { }
});
