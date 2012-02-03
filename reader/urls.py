from django.conf.urls.defaults import *
from reader.views import *

urlpatterns = patterns('reader.views',
    url(r"^articles/$", ArticleListView.as_view(), name='articles'),
    url(r"^articles/achieved$", AchievedArticleListView.as_view(), name='achieved'),

    url(r'^article/detail/(?P<pk>\d+)$', ArticleDetailView.as_view(), name='article_detail'),
    url(r"^article/subscribe$", 'subscribe', name='subscribe'),
    url(r'^/article/unsubscribe/(?P<article_id>\d+)$', 'unsubscribe', name='unsubscribe'),
    url(r'^subscription/mark-as-read/(?P<article_id>\d+)$', 'mark_as_read', name='mark_as_read'),
    url(r"^subscription/unread/(?P<article_id>\d+)$", 'unread', name='unread'),
    url(r"^achieve/rebuild$", 'rebuild', name='rebuild'),

    url(r"^article/tag$", 'add_tag'),
    url(r"^article/untag$", 'remove_tag'),
    url(r"^article/check-existence$", 'check_existence', name='check_existence'),

    url(r'^article/search/$', SearchedArticleListView.as_view(), name='search'),
)


