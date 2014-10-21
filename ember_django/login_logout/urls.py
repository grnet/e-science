#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Urls for login_logout ember-django application.

@author: Ioannis Stenos, Nick Vrionis
'''

from django.conf.urls import patterns, url
from login_logout import views

urlpatterns = patterns('', url(r'^$', 'login_logout.views.main_page'),
                       url(r'^api/users', views.SessionView.as_view()),

                       )
