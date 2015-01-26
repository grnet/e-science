#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Urls for backend ember-django application.

@author: Ioannis Stenos, Nick Vrionis
"""

from django.conf.urls import patterns, include, url
from django.contrib import admin
import views

urlpatterns = patterns('', url(r'^$', 'backend.views.main_page'),
                       url(r'^admin', include(admin.site.urls)),
                       url(r'^api/users', views.SessionView.as_view()),
                       url(r'^api/orka', views.DatabaseView.as_view()),
                       url(r'^api/clusters', views.StatusView.as_view()),
                       url(r'^api/clusterchoices', views.StatusView.as_view()),
                       # celery test stuff - temporary
                       url(r'^api/jobs', views.JobsView.as_view())
                       )
