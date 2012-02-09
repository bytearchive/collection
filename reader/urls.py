from django.conf.urls.defaults import *
from reader.views import *

urlpatterns = patterns('reader.views',
    url(r"^articles/$", ArticleListView.as_view(), name='articles'),
    url(r"^articles/archived/$", ArchivedArticleListView.as_view(), name='archived'),
    url(r'^article/search/$', SearchedArticleListView.as_view(), name='search'),
    url(r'^article/detail/(?P<pk>\d+)/$', ArticleDetailView.as_view(), name='article_detail'),

    url(r'^article/unsubscribe/$', 'unsubscribe', name='unsubscribe'),
    url(r'^article/archive/$', 'archive', name='archive'),
    url(r"^article/unarchive/$", 'unarchive', name='unarchive'),
    url(r"^article/reload/$", 'reload', name='reload'),

    url(r"^article/tag/$", 'add_tag'),
    url(r"^article/untag/$", 'remove_tag'),
    url(r'^tag/autocomplete/$', 'autocomplete', name='tag_autocomplete'),

    url(r"^ajax/article/subscribe/$", 'subscribe', name='subscribe'),
    url(r"^ajax/article/check-existence/$", 'check_existence'),
    url(r"^ajax/article/reading-count/$", 'reading_count'),
)


