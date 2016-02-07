from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^manage/$', views.manage, name='manage'),
    url(r'^$', views.test, name='test')
]