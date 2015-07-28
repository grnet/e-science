attr = App.attr;
// Model for Orka Clusters Statistics 
// Active and Spawned clusters
App.Statistic = DS.Model.extend({
    spawned_clusters : attr('number'),
    active_clusters : attr('number')
});
// Model for e-science News Items
App.Newsitem = DS.Model.extend({
    news_date : attr('date'),
    news_message : attr('string'),
    news_category : attr('number')
});
