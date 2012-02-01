import logging
import os 
import re
from models import Article, Subscription, Bundle
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from reader.tasks import update_article, create_bundle_task

logger = logging.getLogger(__name__)

# help functions
def _user(request):
    return request.user.get_profile()


def browse(request, css='READING', sub_state='UNREAD', article_state='DONE', template='reader/index.html'):
    user = request.user.get_profile()
    reading_cnt = Subscription.objects.filter(user_profile=user, state='UNREAD', article__state='DONE').count()
    pending_count = Subscription.objects.filter(user_profile=user, article__state='UNBUILD').count() 
    subs = Subscription.objects.filter(user_profile=user, state=sub_state, article__state=article_state).order_by('-created').all()[:50]
   
    pills = {}
    for pill in ['READING', 'ACHIEVE', 'PENDING']:
        pills[pill] = (pill == css and 'active' or '')
    return render(request, template, {'subscriptions': subs, \
        'unread_count': reading_cnt , \
        'pending_count': pending_count, \
        'pills': pills
    })

def index(request):
    return browse(request, 'READING', 'UNREAD')

def achieve(request):
    return browse(request, 'ACHIEVE', 'ACHIEVE')
   
# /article/pending
def article_pending(request):
    return browse(request, 'PENDING', 'UNREAD', 'UNBUILD', 'article/pending.html')

# /article/retry
def article_retry(request):
    url = request.POST['url']
    user = _user(request)
    update_article.delay(user.id, url)
    return article_pending(request)

def detail(request, sub_id):
    sub = Subscription.objects.get(pk=sub_id)
    article = sub.article
    return render(request, 'reader/detail.html', {
        'article': article, 
        'subscription': sub
    })

def subscribe(request, article_url):
    article, created = Article.objects.get_or_create(article_url = article_url)
    user = request.user
    sub, created = Subscription.objects.get_or_create(user_profile = user.get_profile(), 
            article = article)

    # launch asyn job to fetch and extract article content
    if article.state == 'UNBUILD':
        update_article.delay(user.id, article_url)
        return HttpResponseRedirect(reverse('reader:browse_articles'))
    return HttpResponseRedirect(reverse('reader:article_detail', args=(sub.id, )))

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
            url = p.strip()
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
    reading_cnt = Subscription.objects.filter(state='UNREAD').count()
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
    sub.state = change_to
    sub.save()

def unsubscribe(request, sub_id):
    sub = Subscription.objects.get(pk=sub_id)
    next_view = sub.state == 'UNREAD' and 'index' or 'view_achieve'
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


def browse_bundles(request):
    user = _user(request)
    bundle_total = Bundle.objects.filter(user_profile=user, state='ALIVE').count()
    bundles = Bundle.objects.filter(user_profile=user, state="ALIVE")
    return render(request, 'bundle/browse.html', {
        'bundle_total': bundle_total,
        'bundles': bundles,
        'browse_class': 'active'
    })


def bundle_create(request, url):
    user = _user(request)  
    create_bundle_task.delay(user.id, url) 
    return HttpResponseRedirect(reverse('reader:browse_bundles'))
   
def bundle_search_or_create(request):
    query = request.POST['query']
    url, tag, words = _normalize_query(query)
    if url:
        return bundle_create(request, url)
    return bundle_create(request, url)

def bundle_detail(request, bundle_id):
    b = Bundle.objects.get(pk=bundle_id)
    return render(request, 'bundle/detail.html', {'bundle': b})
