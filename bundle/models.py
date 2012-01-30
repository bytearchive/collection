from django.db import models
from reader.models import DateSupportModel, UserProfile, Subscription
from taggit.managers import TaggableManager

class Bundle(DateSupportModel):
    STATES = (
        (u'ALIVE', u'alive'),
        (u'REMOVED', u'removed')
    )
    user_profile = models.ForeignKey(UserProfile)
    title = models.CharField(max_length=200)
    tag_manager = TaggableManager()
    subscriptions = models.ManyToManyField(Subscription)
    state = models.CharField(max_length=20, choices=STATES, default=u"ALIVE") 

    def _get_tags(self):
        return self.tag_manager.all()
    tags = property(_get_tags)

    def __unicode__(self):
        return "bundle: %s" % (self.title)
