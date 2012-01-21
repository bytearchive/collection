from django.db import models
from django.contrib.auth.models import User


class Article(models.Model):
    site_url = models.CharField(max_length=200)
    
    article_url = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    content = models.TextField()

    owner = models.ForeignKey(User)
    updated = models.DateTimeField('date upated', auto_now=True, auto_now_add=True)
    created = models.DateTimeField('date created', auto_now_add=True)
