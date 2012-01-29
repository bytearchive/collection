from django.conf.urls.defaults import *

urlpatterns = patterns('reader.views',
    url(r"^$", 'index'),
    (r'^(?P<article_id>\d+)/$', 'detail'),
    (r'^create/$', 'create'),
)
