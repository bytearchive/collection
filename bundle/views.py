import logging
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from BeautifulSoup import BeautifulSoup as Soup
from models import Bundle
from reader.models import UserProfile, Article, Subscription
from reader.extractor import _inner_text


logger = logging.getLogger(__name__)


def browse(request):
    return render(request, 'bundle/browse.html', {'create_class': 'active'})


def create(request):
    text = request.POST['bundle_text']
    soup = Soup(text)
    
    b_title = _inner_text(soup.find('h2'))
    b_tags = [s.strip() for s in _inner_text(soup.find('p')).split(',')]
    b = Bundle.objects.create(title=b_title, user_profile=request.user.get_profile())

    subs = []
    for elem in soup.findAll('a'):
        a, created = Article.objects.get_or_create(article_url=elem['href'])
        s, created = Subscription.objects.get_or_create(article = a, user_profile=b.user_profile)
        subs += [s]
    b.subscriptions = subs
    b.tag_manager.add(*b_tags)
    b.save()

    return HttpResponseRedirect(reverse('bundle:browse'), )
   
