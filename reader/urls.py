from django.conf.urls.defaults import *

urlpatterns = patterns('reader.views',
    url(r"^$", 'index', name='index'),
    url(r'^search_or_subscribe/$', 'search_or_subscribe', name='search_or_subscribe'),
    url(r'^unsubscribe/(?P<sub_id>\d+)$', 'unsubscribe', name='unsubscribe'),

    url(r"^article/$", 'browse', name='browse_articles'),
    url(r"^achieve/achieve$", 'achieve', name='view_achieve'),
    url(r"^achieve/pending$", 'article_pending', name='article_pending'),
    url(r"^achieve/retry$", 'article_retry', name='article_retry'),
    url(r'^article/detail/(?P<sub_id>\d+)$', 'detail', name='article_detail'),

    url(r'^subscription/mark-as-read/(?P<sub_id>\d+)$', 'mark_as_read', name='mark_as_read'),
    url(r"^subscription/unread/(?P<sub_id>\d+)$", 'unread', name='unread'),
    url(r"^subscription/tag$", 'add_tag'),
    url(r"^subscription/untag$", 'remove_tag'),
    url(r"^subscription/check-existence$", 'sub_check_existence', name='sub_check_existence'),
    url(r"^subscription/toggle$", 'sub_toggle', name='sub_toggle'),

    url(r"^bundle/$", 'browse_bundles', name='browse_bundles'),
    url(r"^bundle/detail/(?P<bundle_id>\d+)$", 'bundle_detail', name='bundle_detail'),
    url(r'^bundle/bundle_search_or_create$', 'bundle_search_or_create', name='bundle_search_or_create'),
)


