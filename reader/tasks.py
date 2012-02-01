from celery.decorators import task
from celery.task.sets import subtask
from reader.models import Article, Bundle, Subscription, UserProfile
from reader.extractor import get_article, get_article_meta, BundelExtractor
from urllib2 import urlopen


@task(ignore_result=True)
def update_article(user_id, url):
    logger = update_article.get_logger()
    logger.info('starting update article task: ' + url)
    fetch_page.delay(user_id, url, callback=subtask(update_article_task))

@task(ignore_result=True)
def fetch_page(user_id, url, callback=None):
    logger = fetch_page.get_logger()
    logger.info('fetch page: ' + url)
    html = urlopen(url).read()
    if callback:
        subtask(callback).delay(user_id, url, html)

@task(ignore_result=True)
def update_article_task(user_id, url, html):
    logger = update_article_task.get_logger()
    logger.info('parse html: ' + url)
    article, created = Article.objects.get_or_create(article_url=url)
    content = get_article(html)
    title, author, published = get_article_meta(html)
    article.title = title
    article.author = author
    article.published = published
    article.state = "DONE"
    article.content = content
    article.save()

@task(ignore_result=True)
def analysis_bundle_task(user_id, url, html, callback=None):
    logger = analysis_bundle_task.get_logger()
    logger.info('analysis bundle task ' + url)
    extractor = BundelExtractor(html)
    extractor.extract()
    b, created = Bundle.objects.get_or_create(user_profile_id=user_id, url=url)
    b.content = extractor.content
    b.title = extractor.title
    if extractor.tags:
        b.tag_manager.add(*extractor.tags)
    if callback:
        for href in extractor.urls:
            article, article_created = Article.objects.get_or_create(article_url=href)
            sub, created = Subscription.objects.get_or_create(user_profile_id=user_id, article=article)
            b.subscriptions.add(sub)
            if article_created:
                subtask(callback).delay(user_id, href)
    b.save()

@task(ignore_result=True)
def create_bundle_task(user_id, url):
    logger = create_bundle_task.get_logger()
    logger.info('staring create bundle task ' + url)
    fetch_page.delay(user_id, url, callback=subtask(analysis_bundle_task, 
        callback=subtask(fetch_page, callback=subtask(update_article_task))))
