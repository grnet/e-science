App.Ticker = Ember.Object.extend({
	seconds : 0,
	minutes : 0,
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
		Ember.run.cancel(this.get('timer'));
	},
	// Starts the timer, i.e. executes the `onTick` function every interval.
	start : function() {
		this.set('timer', this.schedule(this.get('onTick')));
	},
	// overriden with the function we want to execute where the Timer object is instantiated
	// example: var metro = App.Metronome.create({seconds:3, onTick: function(){console.log('tock!');}});
	// metro.reopen({seconds: 5, onTick: function(){console.log('ding');}});
	onTick : function() {
	}
});
