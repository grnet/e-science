Orka.CPUSelButView = Ember.View.extend({
    tagName: 'button',
    classNameBindings: [':emberbutton'],
    attributeBindings: ['disabled'],
    click: function () {
        this.get('controller').send('cpu_selection', this.get('name'));
    }
});