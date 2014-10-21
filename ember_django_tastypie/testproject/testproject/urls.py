from django.conf.urls import patterns, include, url
from django.contrib import admin
from tastypie.api import Api

from testapp import resources

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(resources.TesterResource())


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'testproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'testapp.views.main_page'),
    (r'^api/', include(v1_api.urls)),
)
