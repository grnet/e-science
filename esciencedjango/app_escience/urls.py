from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from app_escience import views

urlpatterns = patterns('',
    url(r'^$', 'app_escience.views.main_page'),
    url(r'^login', views.SessionView.as_view()),
    url(r'^users', views.SessionView.as_view()),

)
