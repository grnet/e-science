#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' ROOT_URLCONF file of the project'''

from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns('', url(r'^admin/', include(admin.site.urls)),
                       url(r'^', include('login_logout.urls')),
                       )
