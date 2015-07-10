#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Register the models that will be viewable in
administrator backend of Django.
"""

from django.contrib import admin
from django import forms
from django.forms import Textarea
from backend.models import *

# Customize Django admin image_components form field for long text.
class OrkaImageForm(forms.ModelForm):
    class Meta:
        model = OrkaImage
        fields = '__all__'
        widgets = {'image_components': forms.Textarea(attrs={'cols':'80'}),} # 'rows':10 is default
        help_texts = {'image_components': 'Component metadata in json.dumps format.',}
 
class OrkaImageAdmin(admin.ModelAdmin):
    form = OrkaImageForm
    

admin.site.register(UserInfo)
admin.site.register(UserLogin)
admin.site.register(ClusterInfo)
admin.site.register(Token)
admin.site.register(PublicNewsItem)
admin.site.register(OrkaImage,OrkaImageAdmin)
