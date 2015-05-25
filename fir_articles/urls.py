from django.conf.urls import patterns, url

from fir_articles import views

urlpatterns = patterns('',
    url(r'^$', views.list_articles, name='list'),
    url(r'^(?P<article_id>\d+)/$', views.details, name='details'),
    url(r'^new/$', views.new_article, name='new'),
    url(r'^(?P<article_id>\d+)/comment/$', views.comment, name='comment'),
    url(r'^comment/(?P<comment_id>\d+)$', views.update_comment, name='update_comment'),
    url(r'^comment/$', views.update_comment, name='update_comment_base'),
    url(r'^(?P<article_id>\d+)/comment/(?P<comment_id>\d+)/delete/$', views.delete_comment, name='delete_comment'),
    url(r'^(?P<article_id>\d+)/edit/$', views.edit_article, name='edit'),
    url(r'^(?P<article_id>\d+)/status/(?P<status>[OAD])$', views.change_status, name='change_status'),
    url(r'^(?P<article_id>\d+)/attribute$', views.add_attribute, name='add_attribute'),
    url(r'^(?P<article_id>\d+)/attribute/(?P<attribute_id>\d+)/delete/$', views.delete_attribute, name='delete_attribute'),
)
