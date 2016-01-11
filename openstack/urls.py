"""one_finger URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from openstack import views

urlpatterns = [
    # url(r'^admin/', include(admin.site.urls)),
    # url(r'^openstack/', include(admin.site.urls)),
    # url(r'^$', one_finger_views.index, name='index'),
    url(r'^info/(\d+\.+)$', views.info, name='info'),
    url(r'^test/', views.test, name='test'),
    url(r'^cloud_status/', views.cloud_status, name='cloud_status'),
    url(r'^nova_status/', views.nova_status, name='nova_status'),
    url(r'^neutron_status/', views.neutron_status, name='neutron_status'),
    url(r'^cinder_status/', views.cinder_status, name='cinder_status'),
    url(r'^ceph_status/', views.ceph_status, name='ceph_status'),


]