App.CPUSelButView = Ember.View.extend({
    tagName: 'button',
    classNameBindings: [':emberbutton', ':btn', ':btn-primary', ':btn-xs'],
    attributeBindings: ['disabled', 'name', 'value'],
    click: function () {
        this.get('controller').send('cpu_selection', this.get('value'));
    }
});