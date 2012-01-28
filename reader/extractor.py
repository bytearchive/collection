# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup as Soup
from BeautifulSoup import Tag, NavigableString
from math import floor
import re
   
DEBUG = True 
READABILITY = "readability"

# let re module to cache the used re
PATTERNS = {
    "UNLIKELY_CANDIDATE": r"combx|comment|disqus|foot|header|menu|meta|nav|rss|shoutbox|sidebar|sponsor",
    "MAYBE_CANDIDATE": r"and|article|body|column|main",
    "POSITIVE": r"article|body|content|entry|hentry|page|pagination|post|text",
    "NEGATIVE": r"combx|comment|contact|foot|footer|footnote|link|media|meta|promo|related|scroll|shoutbox|sponsor|tags|widget",
    "BLOCK_ELEMENT": r"<(a|blockquote|dl|div|img|ol|p|pre|table|ul)",
    "REPLACE_BR": r"(<br[^>]*>[ \n\r\t]*){2,}",
    "REPLACE_FONT": r"<(\/?)font[^>]*>",
    "TRIM": r"^(\s|&nbsp;)+|(\s|&nbsp;)+$",
    "NORMALIZE": r"\s{2,}",
    "REMOVE_DUP_BREAKS": r"(<br\s*\/?>(\s|&nbsp;?)*){1,}",
    "VIDEO_URL": r"http:\/\/(www\.)?(youtube|vimeo)\.com"
}

def _debug(*argv):
    if DEBUG:
        for c in argv:
            print c, 
        if len(argv):
            print

def _attr(elem, attr):
    val = ""
    try:
        val = elem[attr] 
    except Exception, e:
        pass
    return val

def _has_attr(elem, attr):
    has = True
    try:
        elem[attr]
    except Exception, e:
        has = False
    return has

def is_navigable_string(elem):
    return isinstance(elem, NavigableString)

def _inner_html(soup):
    html = ''
    if not is_navigable_string(soup):
        for c in soup.contents:
            html += c.__str__()
    return html

def _inner_text(elem):
    if is_navigable_string(elem):
        return elem.__str__()
    return ''.join(elem.findAll(text = True))

def non_string_elements(elem):
    if not is_navigable_string(elem):
        for e in elem:
            for c in non_string_elements(e):
                yield c
    if not is_navigable_string(elem):
        yield elem

def get_link_density(elem):
    if is_navigable_string(elem):
        return 0
    links = elem.findAll('a')
    text_total = len(_inner_text(elem))
    links_text_total = 0
    for link in links:
        links_text_total += len(_inner_text(link))
    return text_total > 0 and float(links_text_total) / text_total or 0.0

class Readability(object):
  
    @staticmethod
    def _is_negative_for_article(s):
        return re.search(PATTERNS['NEGATIVE'], s)

    @staticmethod
    def _is_positive_for_article(s):
        return re.search(PATTERNS['POSITIVE'], s)

    @staticmethod
    def _by_heuristic(s):
        readability = 0
        if s:
            readability += Readability._is_positive_for_article(s) and 25 or 0
            readability += Readability._is_negative_for_article(s) and -25 or 0
        return readability

    @staticmethod
    def by_id_and_class(elem):
        readability = Readability._by_heuristic(_attr(elem, 'class'))
        readability += Readability._by_heuristic(_attr(elem, 'id'))
        return readability

    @staticmethod
    def by_name(elem):
        name = elem.name
        score = 0
        if name == 'div':
            score += 5
        elif name in ('pre', 'td', 'blockquote'):
            score += 3
        elif name in ('address', 'ol', 'ul', 'dl', 'dd', 'dt', 'li', 'form'):
            score -= 3
        elif name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'th'):
            score -= 5
        return score

class ArticleCleaner(object):
    """
    clean the extracted article element
    """
    def __init__(self, article):
        super(ArticleCleaner, self).__init__()
        self.article = article
    
    def _remove_attribute(self, attr_name = 'style'):
        elems = self.article.findAll(lambda x: _has_attr(x, attr_name)) 
        for elem in elems:
            del elem[attr_name]

    @staticmethod
    def _remove_dup_breaks(s):
        return re.sub(PATTERNS['REMOVE_DUP_BREAKS'], '<br/>', s)

    @staticmethod
    def _remove_dup_spaces(s):
        return re.sub(PATTERNS['NORMALIZE'], ' ', s)

    @staticmethod
    def _trim_spaces(s):
        return re.sub(PATTERNS['TRIM'], '', s)

    @staticmethod
    def _is_youtube_or_vimeo(s):
        return re.search(PATTERNS['VIDEO_URL'], s)
    
    def _remove_elem(self, name):
        elems = self.article.findAll(name)
        is_embed = name in ('object', 'embed')
        for elem in elems:
            if is_embed and ArticleCleaner._is_youtube_or_vimeo(_inner_html(elem)):
                continue
            elem.extract()

    def _remove_elem_conditionally(self, name):
        """remove elem consider readability score and the elems within it"""
        for elem in self.article.findAll(name):
            readability = Readability.by_id_and_class(elem)
            remove = False

            if readability < 0:
                remove = True
            else:
                text = _inner_text(elem)
                comma_count = len(text.split(',')) + len(text.split(u'，'))
                if comma_count <= 10:
                    p_count = len(elem.findAll('p'))
                    img_count = len(elem.findAll('img'))
                    li_count = len(elem.findAll('li'))
                    input_count = len(elem.findAll('input'))

                    embed_count = len([x for x in elem.findAll('embed') \
                            if ArticleCleaner._is_youtube_or_vimeo(_inner_html(x))])
                    link_density = get_link_density(elem) 
                    text_length = len(text)

                    if img_count > p_count \
                            or li_count > p_count and name != 'ul' and name != 'ol' \
                            or input_count > floor(p_count / 3) \
                            or text_length < 25 and (img_count == 0 or img_count > 2) \
                            or readability < 25 and link_density > 0.2 \
                            or readability >= 25 and link_density > 0.5 \
                            or embed_count == 1 and text_length < 75 \
                            or embed_count > 1:
                                remove = True
            if remove:
                elem.extract()

    def _remove_empty_paragraph(self):
        elems = self.article.findAll('p')
        for p in elems:
            print "===="
            print p.prettify()
            img_embded_obj_count = len(p.findAll(['img', 'embed', 'object']))
            text = ArticleCleaner._trim_spaces(_inner_text(p))
            if img_embded_obj_count == 0 and len(text) == 0:
                print "=== remove empty paragrapy"
                p.extract()

    def clean(self):
        """ clean article inline style for display """
        self._remove_attribute()

        html = ArticleCleaner._remove_dup_breaks(self.article.__str__())
        html = ArticleCleaner._remove_dup_spaces(html)
        html = ArticleCleaner._trim_spaces(html)
        self.article = Soup(html)

        # elem that considered as junk
        junk_elems = ['form', 'object', 'h1', 'iframe']
        self._remove_elem(junk_elems)

        # only one h2 was considered as misuse h1 as title, so remove it
        if len(self.article.findAll('h2')) == 1:
            self._remove_elem('h2')
        
        fishy_elems = ['table', 'ul', 'div']
        self._remove_elem_conditionally(fishy_elems)
        self._remove_empty_paragraph()
        return self.article

class ArticleExtractor(object):
    """extract article elements from HTML"""
    def __init__(self, html):
        super(ArticleExtractor, self).__init__()
        self.html = html
        self.doc = Soup(html)
        self.candidates = None
        self.top_candidate = None
      
    @staticmethod
    def _is_unlikely_candidate(s):
        return re.search(PATTERNS["UNLIKELY_CANDIDATE"], s) and not re.search(PATTERNS["MAYBE_CANDIDATE"], s)

    @staticmethod
    def _is_div_replaceable(s):
        """ a replaceable DIV is the one that do not contain any block elem """
        return not re.search(PATTERNS["BLOCK_ELEMENT"], s)

    def remove_unlikely(self, remove=True):
        """remove unlikely elems and replace DIV with P if no block elem within"""
        elems = [elem for elem in non_string_elements(self.doc)]
        for elem in elems:
            if remove:
                id_and_class = _attr(elem, 'id') + "#" + _attr(elem, 'class')
                if elem.name != 'body' and ArticleExtractor._is_unlikely_candidate(id_and_class):
                    _debug('remove unlikely candidate: ', id_and_class)
                    elem.extract()
                    continue

            if elem.name == 'div' and ArticleExtractor._is_div_replaceable(_inner_html(elem)):
                _debug('replace div to p: ',  _attr(elem, 'id'))
                p = Tag(self.doc, 'p')
                for i, tag in enumerate(elem.contents):
                    p.insert(i, tag)
                elem.replaceWith(p)

    def init_readability(self, elem):
        readability = Readability.by_name(elem)
        readability += Readability.by_id_and_class(elem)
        elem[READABILITY] = readability
        self.candidates += [elem]
        #_debug('adding readability for ', _attr(elem, id))

    def compute_readability_score(self):
        """ compute readability score basded on P elem """
        paragraphs = self.doc.findAll('p')
        self.candidates = []
        for p in paragraphs:
            text = _inner_text(p)
            if len(text) < 25:
                continue

            parent_elem = p.parent
            if not _has_attr(parent_elem, READABILITY):
                self.init_readability(parent_elem)

            grandparent_elem = parent_elem.parent
            if not _has_attr(grandparent_elem, READABILITY):
                self.init_readability(grandparent_elem)

            # default value for P elem
            readability = 1
            # comma count
            readability += len(text.split(',')) 
            # for chinese chars
            readability += len(text.split(u'，'))      
            # max 3 points for article length
            readability += min(3, floor(len(text) / 3))

            parent_elem[READABILITY] += readability
            grandparent_elem[READABILITY] += readability / 2
        _debug('candidates count: ', len(self.candidates))

    def find_candidate(self):
        """scale readability score by link density and find the best candidate"""
        top_candidate = None
        for c in self.candidates:
            c[READABILITY] *= (1.0 - get_link_density(c))
            if not top_candidate or c[READABILITY] > top_candidate[READABILITY]:
                top_candidate = c
        _debug('top candidate: ', top_candidate.name, ' [id] ', _attr(top_candidate, 'id'), ' [class]', _attr(top_candidate, 'class'))
        #print top_candidate.prettify()

        # use body if top_candidate not found
        if top_candidate is None:
            top_candidate = self.doc.html.body
            init_readability(top_candidate)
        self.top_candidate = top_candidate

    def merge_related_elems(self):
        """ search through sibling for related contents """
        article = Soup('<div></div>')
        index = 0
        threshold = max(10, self.top_candidate[READABILITY] * 0.2)
        siblings = [elem for elem in self.top_candidate.parent.contents]
        for elem in siblings:
            append = False
            if elem is self.top_candidate:
                append = True
            elif _has_attr(elem, READABILITY) and elem[READABILITY] >= threshold:
                append = True
            elif is_navigable_string(elem) or elem.name == 'p':
                text = _inner_text(elem)
                text_length = len(text)
                link_density = get_link_density(elem)
                if text_length >= 80 and link_density < 0.25:
                    append = True
                elif text_length < 80 and link_density < 1e-5 and re.search(r'\.( |$)', text):
                    append = True

            if append:
                _debug("sibling found: ", _attr(elem, 'id'), ' ', _attr(elem, 'class'))
                article.insert(index, elem)
                index += 1
        self.article = article

    def extract(self, remove=True):
        self.remove_unlikely(remove)
        self.compute_readability_score()
        self.find_candidate()
        if self.top_candidate:
            self.merge_related_elems()
        return self.article



def extract(file_path = "two.html"):
    with open(file_path, "r") as file:
        html = ''.join(file.readlines())
    get_article(html)
    get_title(html)

def get_article(html):
    article = ArticleExtractor(html).extract()
    article = ArticleCleaner(article).clean()
    return article.__str__()

def get_title(html):
    soup = Soup(html)
    title = soup.find('h1')

    if title is None:
        return ''
   
    text = _inner_text(title)
    text = ArticleCleaner._remove_dup_spaces(text)
    text = ArticleCleaner._trim_spaces(text)
    #print text
    _debug('title:', text)
    return text

if __name__ == '__main__':
    extract()
