from django.http import HttpResponse
from models import Article
import urllib2 
from pyquery import PyQuery as pq

def detail(request, article_id):
    article = Article.objects.get(pk=article_id)
    return HttpResponse(article.content)

def create(request):
    article_url = request.POST['article_url']
    page = pq(urllib2.urlopen(article_url).read())
    content = page('.post')

    print request.user.username

    article = Article()
    article.site_url = urllib2.Request(article_url).get_host()
    article.article_url = article_url
    article.content = content
    article.owner = request.user
    article.save()

    return HttpResponse(str(content))
