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


def validate_json(payload):
    try:
        json_object = loads(payload, 'utf-8')
    except ValueError, e:
        raise ValidationError('%s is not valid Json' % payload)

# Customize Django admin image_components form field for long text.
class OrkaImageForm(forms.ModelForm):
    image_components = forms.CharField(validators=[MaxLengthValidator(4080),validate_json], \
                                       widget=Textarea(attrs={'cols':'80'}), \
                                       help_text='VM Image Component metadata info in json.dumps format.',required=False)
    class Meta:
        model = OrkaImage
        fields = '__all__'
 
class OrkaImageAdmin(admin.ModelAdmin):
    form = OrkaImageForm
    
# Customize Django admin image_components form field for long text.
class VreImageForm(forms.ModelForm):
    image_components = forms.CharField(validators=[MaxLengthValidator(4080),validate_json], \
                                       widget=Textarea(attrs={'cols':'80'}), \
                                       help_text='VRE Image Component metadata info in json.dumps format.',required=False)
    image_min_reqs = forms.CharField(validators=[MaxLengthValidator(2040),validate_json], \
                                       widget=Textarea(attrs={'cols':'80','rows':'1'}), \
                                       help_text='VRE Image minimum requirements info in json.dumps format.',required=False)
    image_faq_links = forms.CharField(validators=[MaxLengthValidator(2040),validate_json], \
                                       widget=Textarea(attrs={'cols':'80','rows':'3'}), \
                                       help_text='VRE Image faq links in json.dumps format.',required=False)
    class Meta:
        model = VreImage
        fields = '__all__'
 
class VreImageAdmin(admin.ModelAdmin):
    form = VreImageForm
    

admin.site.register(UserInfo)
admin.site.register(UserLogin)
admin.site.register(ClusterInfo)
#admin.site.register(Token)
admin.site.register(PublicNewsItem)
admin.site.register(OrkaImage,OrkaImageAdmin)
admin.site.register(VreImage,VreImageAdmin)
admin.site.register(VreImageCategory)
admin.site.register(VreServer)
admin.site.register(Dsl)
