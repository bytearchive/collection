import urllib2 
import re
import logging
from models import Article, Subscription
from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from extractor import get_article, get_article_meta
from django.db.models import Q

logger = logging.getLogger(__name__)

def browse(request, sub_state):
    reading_cnt = Subscription.objects.filter(subscription_state='UNREAD').count()
    subs = Subscription.objects.filter(subscription_state=sub_state).order_by('-created').all()[:50]
    reading_class = sub_state == 'UNREAD' and 'active' or ''
    achieve_class = sub_state == 'ACHIEVE' and 'active' or ''
    return render(request, 'reader/index.html', {'subscriptions': subs, \
        'unread_count': reading_cnt , \
        'reading_class': reading_class, \
        'achieve_class': achieve_class
    })

def index(request):
    return browse(request, 'UNREAD')

def achieve(request):
    return browse(request, 'ACHIEVE')
    
def detail(request, sub_id):
    sub = Subscription.objects.get(pk=sub_id)
    article = sub.article
    return render(request, 'reader/detail.html', {
        'article': article, 
        'subscription': sub,
        'tags': sub.tags
    })

def subscribe(request, article_url):
    html = urllib2.urlopen(article_url).read()

    site_url = urllib2.Request(article_url).get_host()
    content = get_article(html)
    title, author, published = get_article_meta(html)
    article = Article.objects.create(site_url = site_url,
        article_url = article_url,
        title = title,
        author = author,
        published = published,
        content = content)

    user = request.user
    Subscription.objects.create(user_profile = user.get_profile(), 
            article = article)
    return HttpResponseRedirect(reverse('reader:article_detail', args=(article.id, )))

def _normalize_query(query_string):
    findterms=re.compile(r'"([^"]+)"|(\S+)').findall
    normspace=re.compile(r'\s{2,}').sub
    parts = [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]
    
    url = None
    tags = []
    words = []
    is_url = re.compile(r'\S+://\S+').search
    for p in parts:
        if p[:1] == '#':
            tags += [p[1:]]
        elif is_url(p):
            url = p
        else:
            words += [p]
    return url, tags, words

def search(request, tags, words):
    user = request.user
    q = Q(user_profile=user)
    if tags:
        q &= Q(tags__name__in=tags)
    for word in words:
        q &= Q(article__title__icontains=word)
    subs = Subscription.objects.filter(q).order_by('-created')
    reading_cnt = Subscription.objects.filter(subscription_state='UNREAD').count()
    search_result_count = len(subs)
    query_text = " ".join(['#'+t for t in tags] + words)
    return render(request, 'reader/index.html', {'subscriptions': subs, \
                'unread_count': reading_cnt , \
                'search_result_count': search_result_count, 
                'query_text': query_text
            })

def search_or_subscribe(request):
    query = request.POST['query']
    url, tags, words = _normalize_query(query)
    if url:
        return subscribe(request, url)
    else:
        return search(request, tags, words)

def _change_subscription_state(sub_id, change_to='UNREAD'):
    sub = Subscription.objects.get(pk=sub_id)
    sub.subscription_state = change_to
    sub.save()

def unsubscribe(request, sub_id):
    sub = Subscription.objects.get(pk=sub_id)
    next_view = sub.subscription_state == 'UNREAD' and 'index' or 'view_achieve'
    _change_subscription_state(sub_id, 'REMOVED')
    return HttpResponseRedirect(reverse('reader:' + next_view))

def mark_as_read(request, sub_id):
    _change_subscription_state(sub_id, 'ACHIEVE')
    return HttpResponseRedirect(reverse('reader:index'))

def unread(request, sub_id):
    _change_subscription_state(sub_id, 'UNREAD')
    return HttpResponseRedirect(reverse('reader:view_achieve'))

def _tag_changed(request):
    tag = request.POST['tag_name']
    sub_id = int(request.POST['sub_id'])
    sub = Subscription.objects.get(pk=sub_id)
    return sub, tag

def add_tag(request):
    sub, tag = _tag_changed(request)
    sub.tag_manager.add(tag);
    return HttpResponse('success')

def remove_tag(request):
    sub, tag = _tag_changed(request)
    sub.tag_manager.remove(tag);
    return HttpResponse('success')
