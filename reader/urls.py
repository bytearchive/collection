from django.conf.urls.defaults import *

urlpatterns = patterns('reader.views',
    url(r"^$", 'index', name='index'),
    url(r"^achieve/$", 'achieve', name='view_achieve'),
    url(r'^search_or_subscribe/$', 'search_or_subscribe', name='search_or_subscribe'),
    url(r'^unsubscribe/(?P<sub_id>\d+)$', 'unsubscribe', name='unsubscribe'),

    url(r'^article/detail/(?P<sub_id>\d+)$', 'detail', name='article_detail'),

    url(r'^subscription/mark-as-read/(?P<sub_id>\d+)$', 'mark_as_read', name='mark_as_read'),
    url(r"^subscription/unread/(?P<sub_id>\d+)$", 'unread', name='unread'),
    url(r"^subscription/tag$", 'add_tag'),
    url(r"^subscription/untag$", 'remove_tag'),
)


