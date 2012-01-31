from celery.decorators import task
from celery.task.sets import subtask
from reader.models import Article
from reader.extractor import get_article, get_article_meta
from urllib2 import urlopen


@task(ignore_result=True)
def update_article(url):
    logger = update_article.get_logger()
    logger.info('starting update article task: ' + url)
    fetch_page.delay(url, callback=subtask(parse_html))

@task(ignore_result=True)
def fetch_page(url, callback=None):
    logger = fetch_page.get_logger()
    logger.info('fetch page: ' + url)
    html = urlopen(url).read()
    if callback:
        subtask(callback).delay(url, html)

@task(ignore_result=True)
def parse_html(url, html):
    logger = parse_html.get_logger()
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
