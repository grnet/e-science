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
// Model for e-science Faq Items
App.Faqitem = DS.Model.extend({
    faq_date : attr('date'),
    faq_question : attr('string'),
    faq_answer : attr('string'),
    faq_category : attr('number')
});
// Model for application settings
App.Setting = DS.Model.extend({
   section : attr('string'),
   property_name : attr('string'),
   property_value : attr('string'),
   comment : attr('string') 
});
