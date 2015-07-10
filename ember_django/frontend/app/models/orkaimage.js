attr = App.attr;
// Model used for retrieving OrkaImage information from backend DB
App.Orkaimage = DS.Model.extend({
    image_name : attr('string'), // OrkaImage name
    image_pithos_uuid : attr('string'), // Linked Pithos Image UUID
    image_components : attr('string'), // Stringified OrkaImage Components metadata (json.dumps)
    active_image : function() {// TODO: see if we can avoid hardcoding
        var name = this.get('image_name');
        if (name == 'Cloudera-CDH-5.4.2') {
            return true;
        } else {
            return false;
        }
    }.property('image_name'),

    image_href : function() {
        var uuid = this.get('image_pithos_uuid');
        return '#' + uuid;
    }.property('image_pithos_uuid')
});
