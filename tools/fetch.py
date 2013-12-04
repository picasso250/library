#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, time, thread, datetime
import pickle, re
import urllib, httplib, contextlib, random
from Cookie import SimpleCookie
from contextlib import closing 
import fetchlib

from HTMLParser import HTMLParser

# parser for inner page
class TianyaBookContentHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.last_tag = None
        self.title = None
    def handle_starttag(self, tag, attrs):
        self.last_tag = tag
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        if self.last_tag == 'pre':
            content = data
            content = re.split(r'\r\n\r\n', content)
            content = ['<p>' + re.sub(r'\r\n', '', x) + '</p>' for x in content]
            content = '\n'.join(content)
            self.content = content
        if self.last_tag == 'title' and self.title is None:
            data = re.split('---', data)
            self.title = data[0]

# parser for toc
class TianyaBookTocHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.last_tag = None
        self.title_pass = False
        self.chapters_link = []
        self.chapters_title = []
        self.first_data = True
    def handle_starttag(self, tag, attrs):
        self.last_tag = tag
        if tag == 'font':
            for (k, v) in attrs:
                if k == 'size' and v == '+3':
                    self.title_pass = True
        if tag == 'a':
            self.first_data = True
        if self.title_pass and tag == 'table':
            self.in_links_table = True
        if self.title_pass and self.last_tag == 'a' and self.first_data == True and self.in_links_table:
            self.chapters_link.append(attrs[0][1])
    def handle_endtag(self, tag):
        if self.title_pass and tag == 'table' and self.in_links_table == True:
            self.in_links_table = False
    def handle_data(self, data):
        if self.title_pass and self.last_tag == 'a' and self.first_data == True and self.in_links_table:
            self.chapters_title.append(data)
            self.first_data = False

# parser for inner toc
class TianyaBookInnerTocHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.last_tag = None
        self.chapters_link = []
        self.chapters_title = []
        self.in_content = False
    def handle_starttag(self, tag, attrs):
        self.last_tag = tag
        if tag == 'hr':
            if not self.in_content:
                self.in_content = True
            else:
                self.in_content = False
        if self.in_content and tag == 'a':
            self.chapters_link.append(attrs[0][1])
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        if self.in_content == True and len(data.strip()) > 0 and self.last_tag == 'a':
            self.chapters_title.append(data.strip())

class XcFetch(object):

    def fetch_save_page(self, root, host, path):
        html = fetchlib.fetch_html(host, path)
        print html
        parser = TianyaBookContentHTMLParser()
        parser.feed(html)

        f = open(root+'/'+parser.title+'.html', 'w')
        with closing(f):
            f.write(parser.content)

    def fetch_toc(self, host, path):
        html = fetchlib.fetch_html(host, path)
        parser = TianyaBookTocHTMLParser()
        parser.feed(html)
        parser.chapters_link = [path+x for x in parser.chapters_link]
        return parser

    def fetch_recursive(self, root, host, path):
        parser = self.fetch_toc(host, path)
        for x in parser.chapters_title:
            print x 
        print parser.chapters_link
        self.save_toc(root, parser.chapters_title)

        for x in parser.chapters_link:
            self.fetch_save_chapter(root, host, x)

    def save_toc(self, root, titles):
        chapters = ['<a href="'+x+'.html">'+x+'</a>' for x in titles]
        if not os.path.exists(root):
            os.makedirs(root)
        f = open(root+'/index.html', 'w')
        with closing(f):
            f.write('\n'.join(chapters))

    def fetch_save_chapter(self, root, host, path):
        html = fetchlib.fetch_html(host, path)
        # html = Cache().get('html').decode('gbk').encode('utf-8')
        print html
        if self.is_page(html):
            self.fetch_save_page(root, host, path)
        else:
            self.fetch_save_chapter_small(root, html)

    def is_page(self, html):
        regex = re.compile('<pre>', re.IGNORECASE)
        return regex.search(html)

    def fetch_save_chapter_small(self, root, host, path, html):
        regex = re.compile(r'<HR\b.+?<HR\b.*?>', re.IGNORECASE | re.DOTALL)
        m = regex.search(html)
        content = m.group(0)
        parser = TianyaBookInnerTocHTMLParser()
        parser.feed(html);
        baselink = os.path.dirname(path)
        chapters_link = [baselink+'/'+x for x in parser.chapters_link]
        print chapters_link
        for x in parser.chapters_title:
            print x

        return content

root = '../book/十日谈'
host = 'www.tianyabook.com'
path = '/waiguo2005/b/bujiaqiu/srt/010.htm'
    
xcfetch = XcFetch()
path = '/waiguo2005/b/bujiaqiu/srt/'
# html = xcfetch.fetch_toc(host, path)
# html = xcfetch.fetch_save_page(root, host, path)
xcfetch.fetch_recursive(root, host, path)
path = '/waiguo2005/b/bujiaqiu/srt/0001.htm'
# xcfetch.fetch_save_chapter(root, host, path)
path = '/waiguo2005/b/bujiaqiu/srt/1.html'
# html = fetchlib.fetch_html(host, path);
# html = fetchlib.Cache().get('html').decode('gbk').encode('utf-8')
# xcfetch.fetch_save_chapter_small(root, host, path, html)
