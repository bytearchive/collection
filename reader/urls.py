from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('reader.views',
    url(r"^$", 'index'),
    (r'^(?P<article_id>\d+)/$', 'detail'),
    (r'^create/$', 'create'),
)
