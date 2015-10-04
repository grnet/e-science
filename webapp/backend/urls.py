#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Urls for backend ember-django application.

@author: Ioannis Stenos, Nick Vrionis
"""

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import SessionView, StatusView, JobsView, HdfsView, MainPageView, \
StatisticsView, NewsView, OrkaImagesView, VreServerView, VreImagesView, DslView
admin.site.site_header = "GRNET e-Science Administration"
admin.site.site_title = admin.site.site_header
admin.site.index_title = ''

urlpatterns = patterns('', url(r'^$', MainPageView.as_view()),
                       url(r'^api/statistics', StatisticsView.as_view()),
                       url(r'^api/newsitems', NewsView.as_view()),
                       url(r'^api/orkaimages', OrkaImagesView.as_view()),
                       url(r'^api/vreimages', VreImagesView.as_view()),
                       url(r'^admin', include(admin.site.urls)),
                       url(r'^api/users', SessionView.as_view()),
                       url(r'^api/clusters', StatusView.as_view()),
                       url(r'^api/clusterchoices', StatusView.as_view()),
                       url(r'^api/jobs', JobsView.as_view()),
                       url(r'^api/vreservers', VreServerView.as_view()),
                       url(r'^api/dsls', DslView.as_view()),
                       url(r'^api/hdfs', HdfsView.as_view())
                       )

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += patterns('',
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     )
