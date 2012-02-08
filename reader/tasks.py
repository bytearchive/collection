from celery.decorators import task
from reader.models import Article, UserProfile
from reader.extractor import get_article, get_article_meta

@task(ignore_result=True)
def process_article_task(user_id, url, html):
    logger = process_article_task.get_logger()
    logger.info('start processing article: ' + url)
    
    try:
        user = UserProfile.objects.get(pk=user_id)
        article, created = Article.objects.get_or_create(user=user, url=url)
        content = get_article(url, html)
        title, author, published = get_article_meta(html)
        article.title = title
        article.author = author
        article.published = published
        article.content = content
        article.save()
    except Exception, e:
        logger.error('process article error: ' + url)
        logger.error(str(e))
