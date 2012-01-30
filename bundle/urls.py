from django.conf.urls.defaults import *

urlpatterns = patterns('bundle.views',
    url(r"^$", 'browse', name='browse'),
    url(r"^create/$", 'create', name='create'),
)


