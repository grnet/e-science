from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from app_escience import views

urlpatterns = patterns('',
    #url(r'^(?P<token>\S+)/token/$', views.get_token, name='get_token'),
    url(r'^$', views.SessionView.as_view()),

)
