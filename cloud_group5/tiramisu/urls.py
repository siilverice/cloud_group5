from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.home, name='home'),
	url(r'^login/$', views.login, name='login'),
	url(r'^logout/$', views.logout, name='logout'),
	url(r'^loginsuccess/$', views.loginsuccess, name='loginsuccess'),
    url(r'^index/$', views.index, name='index'),
    url(r'^manage/$', views.manage, name='manage'),
    url(r'^details/$', views.showdetails, name='showdetails'),
    url(r'^requirements/$', views.change_requirements, name='change_requirements'),
    url(r'^register/$', views.register, name='register'),
    url(r'^registersuccess/$', views.registersuccess, name='registersuccess'),
    url(r'^move/$', views.move, name='move'),
    url(r'^turnoff/$', views.turnoff, name='turnoff'),
    url(r'^turnon/$', views.turnon, name='turnon'),
    url(r'^cancel/$', views.cancel, name='cancel'),
    url(r'^createvm/$', views.createvm, name='createvm'),
    url(r'^checkavl/$', views.vmname_availability, name='vmname_availability'),
    url(r'^createvmsuccess/$', views.createvmsuccess, name='createvmsuccess'),
    url(r'^servererror/$', views.servererror, name='servererror'),
    url(r'^shutdown/$', views.shutdown, name='shutdown'),
    url(r'^start/$', views.start, name='start'),
    url(r'^delete/$', views.delete, name='delete'),
    url(r'^rusure/$', views.rusure, name='rusure'),
]