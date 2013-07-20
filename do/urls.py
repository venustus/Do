__author__ = 'venkat'

from django.conf.urls import patterns, url
from do import views

urlpatterns = patterns('',
                       url(r'^task/(?P<task_id>[\d\w]+)/$', views.task_detail, name='task_detail'),
                       url(r'^home/$', views.home, name='home'),
                       url(r'^login/$', views.login_view, name='login'),
                       url(r'^logout/$', views.logout_view, name='logout'),
                       url(r'^people/$', views.people_search, name="people_search"),
                       url(r'^create/$', views.create_task, name='create_task'),
                       url(r'^user/(?P<user_id>[\d\w]+)/$', views.user_detail, name="user_detail"),
                       url(r'^$', views.create_user, name='newdoer'),
)