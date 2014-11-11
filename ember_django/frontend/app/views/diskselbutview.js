Orka.DiskSelButView = Ember.View.extend({
    tagName: 'button',
    classNameBindings: [':emberbutton'],
    attributeBindings: ['disabled'],
    click: function () {
        this.get('controller').send('disk_selection', this.get('name'));
    }
});