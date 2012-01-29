from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from extractor import _inner_text
from BeautifulSoup import BeautifulSoup as Soup

class DateSupportModel(models.Model):
    updated = models.DateTimeField('date upated', auto_now=True, auto_now_add=True)
    created = models.DateTimeField('date created', auto_now_add=True)

    class Meta:
        abstract = True

class Article(DateSupportModel):
    site_url = models.CharField(max_length=200)
    article_url = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __unicode__(self):
        return self.title

    def _get_summary(self): 
        print "========="
        text = _inner_text(Soup(self.content))
        print len(text)
        return text[:150] + "..."
    summary = property(_get_summary)

class UserProfile(DateSupportModel):
    user = models.OneToOneField(User)
    articles = models.ManyToManyField(Article, through="Subscription")

    def __unicode__(self):
        return self.user.username

class Subscription(DateSupportModel):
    SUBSCRIPTION_STATE = (
        (u'UNREAD', u'unread'),
        (u'ACHIEVE', u'achieve')
    )
    user_profile = models.ForeignKey(UserProfile)
    article = models.ForeignKey(Article)
    subscription_state = models.CharField(max_length=20, choices=SUBSCRIPTION_STATE, default="UNREAD") 

    def __unicode__(self):
        return "%s's article: %s" % (self.user_profile.user, self.article.title)

# hook UserProfile with User
def create_user_profile(sender, instance, created, **kwargs):
    if created:
       profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)
