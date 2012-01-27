import urllib2 
from models import Article, Subscription
from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from extractor import get_article, get_title

def index(request):
    articles = list(Article.objects.order_by('-created').all()[:50])
    return render(request, 'reader/index.html', {'articles': articles})
    
def detail(request, article_id):
    article = Article.objects.get(pk=article_id)
    return render(request, 'reader/detail.html', {'article': article})

def create(request):
    article_url = request.POST['article_url']
    html = urllib2.urlopen(article_url).read()

    site_url = urllib2.Request(article_url).get_host()
    content = get_article(html)
    title = get_title(html)
    article = Article.objects.create(site_url = site_url,
            article_url = article_url,
            title = title,
            content = content)

    user = request.user
    Subscription.objects.create(user_profile = user.get_profile(), 
            article = article)
    return HttpResponseRedirect(reverse('reader.views.detail', args=(article.id, )))
