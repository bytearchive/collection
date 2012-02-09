import logging
import re
from reader.models import Article
from reader.tasks import process_article_task
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect 
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from taggit.models import Tag

logger = logging.getLogger(__name__)

def _user(request):
    return request.user.get_profile()

def _get_reading_count(user):
    reading_count = Article.objects.filter(user=user, state='UNREAD', deleted=False).count()
    return reading_count

class ArticleDetailView(DetailView):
    model = Article
    template_name = "reader/article/detail.html"
    context_object_name = "article"

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
      
        article = context['article']
        context['archived'] = not article.is_archived() and 'hidden' or ''
        context['unarchived'] = article.is_archived() and 'hidden' or ''
        return context
    

class ArticleListView(ListView):
    context_object_name = 'article_list'
    template_name = "reader/article/list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ArticleListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        user = _user(self.request)
        return Article.objects.filter(user=user, state='UNREAD', deleted=False)

    def get_context_data(self, **kwargs):
        user = _user(self.request)
        context = super(ArticleListView, self).get_context_data(**kwargs)
        
        context['reading_count'] = _get_reading_count(user)

        self.ping_reading(context)
        return context

    def ping_reading(self, context):
        context['UNREAD'] = 'active' 

class ArchivedArticleListView(ArticleListView):
    def get_queryset(self):
        user = _user(self.request)
        return Article.objects.filter(user=user, state='ARCHIVED', deleted=False)
        
    def ping_reading(self, context):
        context['ARCHIVED'] = 'active' 

class SearchedArticleListView(ArticleListView):

    def _normalize_query(self, query_string):
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

    def get_queryset(self):
        query = self.request.GET['query']
        user = _user(self.request)
        url, tags, words = self._normalize_query(query)

        q = Q(user=user) & Q(deleted=False)
        for word in words:
            q &= Q(title__icontains=word) | Q(content__icontains=word)
        results = Article.objects.filter(q)
        for tag in tags:
            results = results.filter(tags__name__iexact=tag)
        return results.distinct()

       
    def get_context_data(self, **kwargs):
        context = super(SearchedArticleListView, self).get_context_data(**kwargs)
        context['query'] = self.request.GET['query']
        return context

    def ping_reading(self, context):
        context['RESULT'] = 'active' 

def subscribe(req):
    html = req.POST['html']
    url = req.POST['url']
    tags = simplejson.loads(req.POST['tags'])
    user = _user(req)
    article, created = Article.objects.get_or_create(user=user, url=url)
    article.html = html
    article.state = 'UNREAD'
    article.deleted = False
    article.tags.add(*tags);
    article.save()
    process_article_task.delay(user.id, url, html)
    return reading_count(req)

def reload(request):
    user = _user(request)
    a = Article.objects.get(pk=request.POST['article_id'])
    process_article_task.delay(user.id, a.url, a.html)
    return HttpResponseRedirect(reverse('reader:articles'))

def unsubscribe(request):
    article_id = request.POST['article_id'];
    a = Article.objects.get(pk=article_id)
    a.delete()
    return HttpResponseRedirect(reverse('reader:articles'))

def _change_article_state(article_id, change_to='UNREAD'):
    a = Article.objects.get(pk=article_id)
    a.state = change_to
    a.save()

def archive(request):
    article_id = request.POST['article_id'];
    _change_article_state(article_id, 'ARCHIVED')
    return HttpResponseRedirect(reverse('reader:articles'))

def unarchive(request):
    article_id = request.POST['article_id'];
    _change_article_state(article_id, 'UNREAD')
    return HttpResponseRedirect(reverse('reader:archived'))

def _tag_changed(request):
    tag = request.POST['tag_name']
    article_id = int(request.POST['article_id'])
    a = Article.objects.get(pk=article_id)
    return a, tag

def add_tag(request):
    a, tag = _tag_changed(request)
    a.tags.add(tag);
    return HttpResponse('success')

def remove_tag(request):
    a, tag = _tag_changed(request)
    a.tags.remove(tag);
    return HttpResponse('success')

def check_existence(request):
    url = request.GET['url']
    is_saved = False
    if request.user.is_authenticated():
        user = _user(request)
        try:
            sub = Article.objects.get(user=user, url=url, deleted=False)
            is_saved = True
        except Exception, e:
            sub = None
    return HttpResponse(simplejson.dumps({"is_saved": is_saved}))

def autocomplete(req):
    tags = [t.name for t in Tag.objects.all()]
    return HttpResponse(simplejson.dumps({"tags": tags}))

def reading_count(req):
    user = _user(req)
    reading = _get_reading_count(user)
    return HttpResponse(simplejson.dumps({"reading_count": reading}))
