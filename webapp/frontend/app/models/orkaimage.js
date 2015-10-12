attr = App.attr;
// Model used for retrieving OrkaImage information from backend DB
App.Orkaimage = DS.Model.extend({
    image_name : attr('string'), // OrkaImage name
    image_pithos_uuid : attr('string'), // Linked Pithos Image UUID
    image_components : attr('string'), // Stringified OrkaImage Components metadata (json.dumps)
    image_min_reqs : attr('string'), // stringified OrkaImage minimum requirements metadaga (json.dumps)
    image_faq_links : attr('string'), // stringified OrkaImage FAQ links (json.dumps)
    image_init_extra : attr(), // array of extra creation fields
    image_access_url : attr(), // array of access URLs
    image_category : attr('string'), // OrkaImageCategory name (resolving from id at backend)
    image_href : function() {
        var uuid = this.get('image_pithos_uuid');
        return '#' + uuid;
    }.property('image_pithos_uuid')
});
