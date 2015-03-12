#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Urls for backend ember-django application.

@author: Ioannis Stenos, Nick Vrionis
"""

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import SessionView, StatusView, JobsView, HdfsView

urlpatterns = patterns('', url(r'^$', 'backend.views.main_page'),
                       url(r'^admin', include(admin.site.urls)),
                       url(r'^api/users', SessionView.as_view()),
                       url(r'^api/clusters', StatusView.as_view()),
                       url(r'^api/clusterchoices', StatusView.as_view()),
                       url(r'^api/jobs', JobsView.as_view()),
                       url(r'^api/hdfs', HdfsView.as_view())
                       )

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += patterns('',
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     )
