from django.conf.urls.defaults import *
from reader.views import *

urlpatterns = patterns('reader.views',
    url(r"^articles/$", ArticleListView.as_view(), name='articles'),
    url(r"^articles/achieved/$", AchievedArticleListView.as_view(), name='achieved'),
    url(r'^article/detail/(?P<pk>\d+)/$', ArticleDetailView.as_view(), name='article_detail'),

    url(r"^article/subscribe/$", 'subscribe', name='subscribe'),
    url(r'^article/unsubscribe/$', 'unsubscribe', name='unsubscribe'),
    url(r'^article/achieve/$', 'achieve', name='achieve'),
    url(r"^achieve/unachieve/$", 'unachieve', name='unachieve'),
    url(r"^achieve/reload/$", 'reload', name='reload'),

    url(r"^article/tag/$", 'add_tag'),
    url(r"^article/untag/$", 'remove_tag'),
    url(r"^article/check-existence/$", 'check_existence', name='check_existence'),

    url(r'^article/search/$', SearchedArticleListView.as_view(), name='search'),
)


