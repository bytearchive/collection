import logging
from reader.models import Article, UserProfile
from reader.extractor import get_article, get_article_meta

logger = logging.getLogger(__name__)

def process_article_task(user_id, url, html):
    logger.debug('start processing article: ' + url)
    user = UserProfile.objects.get(pk=user_id)
    article, created = Article.objects.get_or_create(user=user, url=url)
    content = get_article(url, html)
    title, author, published = get_article_meta(html)
    article.title = title
    article.author = author
    article.published = published
    article.content = content
    article.save()
