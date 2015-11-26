#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Urls for backend ember-django application.

@author: e-science Dev-team
"""

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import SessionView, StatusView, JobsView, HdfsView, MainPageView, SettingsView, \
StatisticsView, NewsView, FaqView, OrkaImagesView, VreServerView, VreImagesView, DslView, \
ScreensView, VideosView
admin.site.site_header = "GRNET e-Science Administration"
admin.site.site_title = admin.site.site_header
admin.site.index_title = ''

urlpatterns = patterns('', url(r'^$', MainPageView.as_view()),
                       url(r'^api/statistics', StatisticsView.as_view()),
                       url(r'^api/newsitems', NewsView.as_view()),
                       url(r'^api/faqitems', FaqView.as_view()),
                       url(r'^api/screens', ScreensView.as_view()),
                       url(r'^api/videos', VideosView.as_view()),
                       url(r'^api/orkaimages', OrkaImagesView.as_view()),
                       url(r'^api/vreimages', VreImagesView.as_view()),
                       url(r'^admin', include(admin.site.urls)),
                       url(r'^api/settings', SettingsView.as_view()),
                       )

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += patterns('',
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     )
