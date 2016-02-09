from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^manage/$', views.manage, name='manage'),
    url(r'^post/requirements/$', views.change_requirements, name='change_requirements'),
    url(r'^listvm/$', views.listvm, name='listvm'),
]