import urllib2 
from models import Article, Subscription
from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from extractor import get_article, get_article_meta

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
        'tags': sub.tags.all()
    })

def subscribe(request):
    article_url = request.POST['article_url']
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

def unsubscribe(request, sub_id):
    pass

def _change_subscription_state(sub_id, change_to='UNREAD'):
    sub = Subscription.objects.get(pk=sub_id)
    sub.subscription_state = change_to
    sub.save()

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
    sub.tags.add(tag);
    return HttpResponse('success')

def remove_tag(request):
    sub, tag = _tag_changed(request)
    sub.tags.remove(tag);
    return HttpResponse('success')
