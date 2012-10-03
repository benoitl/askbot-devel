"""url patterns for the `windriver` django app"""
from django.conf.urls.defaults import patterns, url
from windriver import views

urlpatterns = patterns('',
    url('^search-login/', views.search_login, name='search_login'),
)
