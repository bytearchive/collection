import urllib2
import re
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from extractor import _inner_text
from BeautifulSoup import BeautifulSoup as Soup
from taggit.managers import TaggableManager

class DateSupportModel(models.Model):
    updated = models.DateTimeField('date upated', auto_now=True, auto_now_add=True)
    created = models.DateTimeField('date created', auto_now_add=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']
        abstract = True

    def delete(self):
        self.deleted = True
        self.save()

class UserProfile(DateSupportModel):
    user = models.OneToOneField(User)

    def __unicode__(self):
        return self.user.username

class Article(DateSupportModel):
    STATES = (
        (u'UNREAD', u'unread'),
        (u'ACHIEVE', u'achieve')
    )
    url = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255, default='')
    author = models.CharField(max_length=100, default='')
    published = models.CharField(max_length=50, default='')
    content = models.TextField()
    html = models.TextField()
    state = models.CharField(max_length=20, choices=STATES, default="UNREAD") 

    user = models.ForeignKey(UserProfile)
    tags = TaggableManager()

    def __unicode__(self):
        return self.url

    def _get_summary(self): 
        text = _inner_text(Soup(self.content))
        text_len = 120
        if re.search('[a-zA-Z]', text[:5]):
            text_len = 240
        return text[:text_len] + "..."
    summary = property(_get_summary)

    def _get_site_url(self):
        return urllib2.Request(self.url).get_host()
    site_url = property(_get_site_url) 

    def _get_url_summary(self):
        url = self.url[:80]
        if len(self.url) > 80:
            url += "..."
        return  url
    url_summary = property(_get_url_summary) 


# hook UserProfile with User
def create_user_profile(sender, instance, created, **kwargs):
    if created:
       profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)
