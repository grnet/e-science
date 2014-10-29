#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Urls for backend ember-django application.

@author: Ioannis Stenos, Nick Vrionis
'''

from django.conf.urls import patterns, include, url
from django.contrib import admin
from backend import views

urlpatterns = patterns('', url(r'^$', 'backend.views.main_page'),
                       url(r'^admin', include(admin.site.urls)),
                       url(r'^api/users', views.SessionView.as_view()),

                       )
