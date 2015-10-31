#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Register the models that will be viewable in
administrator backend of Django.
"""

from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django import forms
from django.forms import Textarea
from django.core import validators
from django.core.validators import MaxLengthValidator
from django.core.exceptions import ValidationError
from django.db.models import ManyToOneRel
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
    image_min_reqs = forms.CharField(validators=[MaxLengthValidator(2040),validate_json], \
                                       widget=Textarea(attrs={'cols':'80','rows':'1'}), \
                                       help_text='VM Image minimum requirements info in json.dumps format.',required=False)
    image_faq_links = forms.CharField(validators=[MaxLengthValidator(2040),validate_json], \
                                       widget=Textarea(attrs={'cols':'80','rows':'3'}), \
                                       help_text='VM Image faq {"label":"url"} links in json.dumps format.',required=False)
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
                                       help_text='VRE Image faq {"label":"url"} links in json.dumps format.',required=False)
    class Meta:
        model = VreImage
        fields = '__all__'


class VreImageAdmin(admin.ModelAdmin):
    form = VreImageForm

# Customize form to enforce case-insensitive unique check
class SettingAdminForm(forms.ModelForm):
    def clean(self):
        _new = True if not self.instance.pk else False
        section = self.cleaned_data['section']
        property_name = self.cleaned_data['property_name']
        breaks_unique = Setting.objects.all().filter(section__iexact=section,property_name__iexact=property_name).exists()
        # do not block updates, only new entries that would be duplicates
        if _new and breaks_unique:
            raise forms.ValidationError('Duplicate section, property_name pair already exists.')
        return self.cleaned_data
        
    class Meta:
        model = Setting
        fields = '__all__'
     
class SettingAdmin(admin.ModelAdmin):
    form = SettingAdminForm

# need to explicitly state not required as admin doesn't follow model convention
# need a related field wrapper to reproduce the default functionality of being able to add new category from faqitem form
class FaqItemForm(forms.ModelForm):
    faq_category = forms.ModelChoiceField(queryset=FaqItemCategory.objects.all(), required=False, help_text='FAQ Item Category')
    def __init__(self, *args, **kwargs):
        super(FaqItemForm, self).__init__(*args, **kwargs)
        rel = ManyToOneRel(self.instance._meta.get_field('faq_category'), FaqItemCategory, 'id') # Django 1.6+
        self.fields['faq_category'].widget = RelatedFieldWidgetWrapper(self.fields['faq_category'].widget, rel, self.admin_site)
    class Meta:
        model = FaqItem
        fields = '__all__'

class FaqItemAdmin(admin.ModelAdmin):
    form = FaqItemForm
    def __init__(self, model, admin_site):
        self.form.admin_site = admin_site 
        super(FaqItemAdmin, self).__init__(model, admin_site)


admin.site.register(Setting,SettingAdmin)
admin.site.register(PublicNewsItem)
admin.site.register(FaqItem,FaqItemAdmin)
admin.site.register(FaqItemCategory)
admin.site.register(ScreenItem)
admin.site.register(ScreenItemCategory)
admin.site.register(VideoItem)
admin.site.register(OrkaImage,OrkaImageAdmin)
admin.site.register(OrkaImageCategory)
admin.site.register(VreImage,VreImageAdmin)
admin.site.register(VreImageCategory)
