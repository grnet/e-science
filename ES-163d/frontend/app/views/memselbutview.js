Orka.MEMSelButView = Ember.View.extend({
    tagName: 'button',
    classNameBindings: [':emberbutton'],
    attributeBindings: ['disabled'],
    click: function () {
        this.get('controller').send('mem_selection', this.get('name'));
    }
});
