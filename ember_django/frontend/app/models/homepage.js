attr = App.attr;
// Model for Orka Clusters Statistics 
// Active and Spawned clusters
App.Statistic = DS.Model.extend({
    spawned_clusters : attr('number'),
    active_clusters : attr('number')
});

App.Newsitem = DS.Model.extend({
    news_date : attr('date'),
    news_message : attr('string'),
    news_category : attr('number')
});
