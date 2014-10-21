from tastypie.resources import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization

from testapp import models

class TesterResource(ModelResource):
    class Meta:
        queryset = models.Tester.objects.all()
        allowed_methods = ['get', 'post']
        always_return_data = True
        authorization= Authorization()