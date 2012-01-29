from django.conf.urls.defaults import *

urlpatterns = patterns('reader.views',
    url(r"^$", 'index'),
    (r"^achieve/$", 'achieve'),
    (r'^(?P<article_id>\d+)$', 'detail'),
    (r'^create/$', 'create'),
    (r'^mark-as-read/(?P<sub_id>\d+)$', 'mark_as_read'),
)
