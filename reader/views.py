import urllib2 
from models import Article
from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from pyquery import PyQuery as pq

def detail(request, article_id):
    article = Article.objects.get(pk=article_id)
    return render(request, 'reader/detail.html', {'article': article})

def create(request):
    article_url = request.POST['article_url']
    page = pq(urllib2.urlopen(article_url).read())
    content = page('.entry-content')

    article = Article()
    article.site_url = urllib2.Request(article_url).get_host()
    article.article_url = article_url
    article.title = page('h1').text()
    article.content = content
    article.owner = request.user
    article.save()

    return HttpResponseRedirect(reverse('reader.views.detail', args=(article.id, )))
