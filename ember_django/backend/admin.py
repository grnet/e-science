#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Register the models that will be viewable in
administrator backend of Django.
"""

from django.contrib import admin
from django import forms
from django.forms import Textarea
from django.core import validators
from django.core.validators import MaxLengthValidator
from django.core.exceptions import ValidationError
from json import loads
from backend.models import *


def validateJSON(payload):
    try:
        json_object = loads(payload, 'utf-8')
    except ValueError, e:
        raise ValidationError('%s is not valid Json' % payload)

# Customize Django admin image_components form field for long text.
class OrkaImageForm(forms.ModelForm):
    image_components = forms.CharField(validators=[MaxLengthValidator(4080),validateJSON], \
                                       widget=Textarea(attrs={'cols':'80'}), \
                                       help_text='Component metadata info in json.dumps format.')
    class Meta:
        model = OrkaImage
        fields = '__all__'
 
class OrkaImageAdmin(admin.ModelAdmin):
    form = OrkaImageForm
    

admin.site.register(UserInfo)
admin.site.register(UserLogin)
admin.site.register(ClusterInfo)
admin.site.register(Token)
admin.site.register(PublicNewsItem)
admin.site.register(OrkaImage,OrkaImageAdmin)
