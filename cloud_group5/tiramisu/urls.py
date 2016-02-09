from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.home, name='home'),
	url(r'^login/$', views.login, name='login'),
    url(r'^index/$', views.index, name='index'),
    url(r'^manage/$', views.manage, name='manage'),
    url(r'^post/requirements/$', views.change_requirements, name='change_requirements'),
    url(r'^listvm/$', views.listvm, name='listvm'),
    url(r'^register/$', views.register, name='register'),
    url(r'^registersuccess/$', views.registersuccess, name='registersuccess'),
]