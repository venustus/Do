__author__ = 'venkat'

from django.conf.urls import patterns, url
from do import views

urlpatterns = patterns('',
                       url(r'^$', views.home, name='home'),
)