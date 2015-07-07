#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Register the models that will be viewable in
administrator backend of Django.
"""

from django.contrib import admin
from backend.models import *

admin.site.register(UserInfo)
admin.site.register(UserLogin)
admin.site.register(ClusterInfo)
admin.site.register(Token)
admin.site.register(VreServer)
