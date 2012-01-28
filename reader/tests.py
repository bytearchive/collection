"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

"""
from django.test import TestCase
from extractor import _inner_text
from extractor import *
from BeautifulSoup import BeautifulSoup as Soup
from BeautifulSoup import Tag
import re

class PythonCommon(TestCase):
    def test_None_add_string(self):
        with self.assertRaises(TypeError):
            "" + None
   
    def test_empty_string_like_false(self):
        with self.assertRaises(Exception):
            if not "":
                raise Exception()

class RegularExprTest(TestCase):
    def test_re_search(self):
        """ dot at line end, or ends with a space """
        self.assertIsNotNone(re.search(r'\.( |$)', '. '))

    def test_remove_dup_spaces(self):
        """ just remember: first params of sub is the replacement string"""
        dup_spaces_re = re.compile(r"\s{2,}")
        replaced = dup_spaces_re.sub(' ', '  aa   bb   cc')
        self.assertEqual(' aa bb cc', replaced)

class UtilFuncTest(TestCase):
    def setUp(self):
        self.doc = ['<html><head><title>Page title</title></head>',
           '<body><p class="para" id="firstpara" align="center">This is paragraph <b>one</b>.',
           '<p id="secondpara" align="blah">This is paragraph <b>two</b>.',
           '</html>']
        self.soup = Soup("".join(self.doc))
    
    def test_link_density(self):
        soup = Soup('<p>1234567890<a>12345</a>12345</p>')
        self.assertEqual(0.25, get_link_density(soup))

    def test_inner_text(self):
        self.assertEqual('This is paragraph one.This is paragraph two.', _inner_text(self.soup.html.body))

class ReadabilityTest(TestCase):
    def setUp(self):
        self.doc = ['<html><head><title>Page title</title></head>',
           '<body><p class="para" id="firstpara" align="center">This is paragraph <b>one</b>.',
           '<p id="secondpara" align="blah">This is paragraph <b>two</b>.',
           '</html>']
        self.soup = Soup("".join(self.doc))

    def test_readability_score_by_name(self):
        div = Tag(self.soup, 'div')
        self.assertEqual(5, Readability.by_name(div))

        form = Tag(self.soup, 'form')
        self.assertEqual(-3, Readability.by_name(form))

    def test_readability_score_by_class_and_id(self):
        div = Tag(self.soup, 'div')
        div['class'] = 'article'
        div['id'] = 'content'
        readability = Readability.by_id_and_class(div)
        self.assertEqual(50, readability)

class ArticleCleanerTest(TestCase):
   
    def test_remove_dup_breaks(self):
        dup_breaks = "<br/><br/>"
        self.assertEqual('<br/>', ArticleCleaner._remove_dup_breaks(dup_breaks))

    def test_remove_dup_spaces(self):
        sps = "  aa    bb   cc  "
        self.assertEqual(' aa bb cc ', ArticleCleaner._remove_dup_spaces(sps))

    def test_trim_spaces(self):
        spaces = "   aa   bb    "
        self.assertEqual('aa   bb', ArticleCleaner._trim_spaces(spaces))

    def test_youtube_url(self):
        youtube = 'http://youtube.com'
        self.assertIsNotNone(ArticleCleaner._is_youtube_or_vimeo(youtube))

    def setUp(self):
        self.doc = ['<html><head><title>Page title</title></head>',
           '<body><p class="para" id="firstpara" align="center">This is paragraph <b>one</b>.',
           '<p id="secondpara" align="blah">This is paragraph <b>two</b>.',
           '</html>']
        self.soup = Soup("".join(self.doc))
        self.body = self.soup.html.body

    def test_remove_elements(self):
        self.assertEqual(2, len(self.body.findAll('p')))
        ac = ArticleCleaner(self.soup)
        ac._remove_elem('p')
        self.assertEqual(0, len(self.body.findAll('p')))

    def test_remove_empty_p(self):
        self.soup = Soup('<p> &nbsp; </p>')
        self.assertEqual(1, len(self.soup.findAll('p')))
        ac = ArticleCleaner(self.soup)
        ac._remove_empty_paragraph()
        self.assertEqual(0, len(self.soup.findAll('p')))


class ArticleExtractorTest(TestCase):
    
    def test_unlikely_candidate(self):
        unlikely = ('header', 'comment', 'menu')
        for s in unlikely:
            self.assertIsNotNone(ArticleExtractor._is_unlikely_candidate(s))

        likely = ('article', 'content')
        for s in likely:
            self.assertIsNone(ArticleExtractor._is_unlikely_candidate(s))

        others = ('aaa', 'bbb')
        for s in others:
            self.assertIsNone(ArticleExtractor._is_unlikely_candidate(s))

    def test_repace_div(self):
        replaceables = ('', '<li></li>')
        for s in replaceables:
            self.assertTrue(ArticleExtractor._is_div_replaceable(s))

        not_replaceables = ('<a></a>', '<div></div>')
        for s in not_replaceables:
            self.assertFalse(ArticleExtractor._is_div_replaceable(s))

    

class BeautifulSoupTest(TestCase):
    def setUp(self):
        self.doc = ['<html><head><title>Page title</title></head>',
           '<body><p class="para" id="firstpara" align="center">This is paragraph <b>one</b>.',
           '<p id="secondpara" align="blah">This is paragraph <b>two</b>.',
           '</html>']
        self.soup = Soup("".join(self.doc))

    def test_non_exist_attr(self):
        """Soup return None for non exist attribute, or KeyError for dict like acess"""
        self.assertEqual(None, self.soup.html.head.id)

        with self.assertRaises(KeyError):
            self.soup.html.head['none']

    def test_auto_closing_tag(self):
        prt = self.soup.html.body.__str__()
        self.assertNotEqual("".join(self.doc), prt, "automatic close P tag")

    def test_create_new_tag(self):
        div = Tag(self.soup, 'div')
        self.assertEqual('<div></div>', div.__str__())

    def test_insert_new_content(self):
        """ IMPORTANT: this is how to replace a element in BeautifulSoup """
        text = '<p>AA<b>one</b></p><p>BB</p>'
        p = Soup(text)
        tags = [t for t in p.contents] # should first collect all tags for insertation
        for t in tags:
            self.soup.html.body.insert(0, t)
        self.assertEqual(4, len(self.soup.html.findAll('p')))

    def test_reference_first_elem(self):
        p_first = self.soup.html.body.p
        self.assertEqual('firstpara', p_first['id'])

    def test_css_class_reference(self):
        p_with_class = self.soup.html.body.p
        self.assertEqual('para', p_with_class['class'])

        with self.assertRaises(KeyError):
            p_without_class = self.soup.html.body.contents[1]
            self.assertEqual('para', p_without_class['class'])

    def test_create_new_soup(self):
        so = Soup('<div></div>')
        self.assertEqual(1, len(so.contents))

        


