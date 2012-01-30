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

    class Meta:
        abstract = True

class Article(DateSupportModel):
    STATES = (
        (u'UNBUILD', u'unbuild'), 
        (u'DONE', u'done'), 
    )
    article_url = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=200, default='')
    author = models.CharField(max_length=50, default='')
    published = models.CharField(max_length=50, default='')
    content = models.TextField(default='')
    state = models.CharField(max_length=20, choices=STATES, default="unbuild") 

    def __unicode__(self):
        return self.title

    def _get_summary(self): 
        text = _inner_text(Soup(self.content))
        text_len = 120
        if re.search('[a-zA-Z]', text[:5]):
            text_len = 240
        return text[:text_len] + "..."
    summary = property(_get_summary)

    def _get_site_url(self):
        return urllib2.Request(self.article_url).get_host()
    site_url = property(_get_site_url) 

class UserProfile(DateSupportModel):
    user = models.OneToOneField(User)
    articles = models.ManyToManyField(Article, through="Subscription")

    def __unicode__(self):
        return self.user.username


class Subscription(DateSupportModel):
    SUBSCRIPTION_STATE = (
        (u'UNREAD', u'unread'),
        (u'ACHIEVE', u'achieve'),
        (u'REMOVED', u'removed')
    )
    user_profile = models.ForeignKey(UserProfile)
    article = models.ForeignKey(Article, unique=True)
    subscription_state = models.CharField(max_length=20, choices=SUBSCRIPTION_STATE, default="UNREAD") 
    tag_manager = TaggableManager()

    def _get_tags(self):
        return self.tag_manager.all()
    tags = property(_get_tags)

    def __unicode__(self):
        return "%s's article: %s" % (self.user_profile.user, self.article.title)

# hook UserProfile with User
def create_user_profile(sender, instance, created, **kwargs):
    if created:
       profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)
