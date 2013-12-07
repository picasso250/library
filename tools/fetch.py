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
        self.content = None
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
        if tag == 'a':
            href = attrs[0][1]
            if is_current_page_link(href) and is_web_page_file(href):
                print href
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

# parser for href link, then we will download them
class CurrentPageHrefHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.last_tag = None
        self.links = []
        self.link = None
        self.first_data = True
        self.is_link = False
    def handle_starttag(self, tag, attrs):
        self.last_tag = tag
        if tag == 'a':
            self.first_data = True
            href = attrs[0][1]
            if is_current_page_link(href) and is_web_page_file(href):
                self.is_link = True
                self.link = {}
                self.link['href'] = href
            else:
                self.is_link = False
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        if self.last_tag == 'a' and self.first_data == True and self.is_link:
            self.link['title'] = data
            self.links.append(self.link)
            self.first_data = False

def is_web_page_file(href):
    name, ext = os.path.splitext(href)
    return (ext == '.html' or ext == '.htm')

def is_current_page_link(href):
    return ( len(os.path.dirname(href)) == 0 and href.find(':') == -1 )

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

def extract_body_inner_html(html):
    regex = re.compile(r'<body\b.+?>(.+)</body>', re.IGNORECASE | re.DOTALL)
    m = regex.search(html)
    return m.group(1)

class XcFetch(object):

    def fetch_save_page(self, root, host, path):
        html = fetchlib.fetch_html(host, path)
        parser = TianyaBookContentHTMLParser()
        parser.feed(html)
        if parser.content is None:
            print html
            print 'content is None'
            return

        f = open(root+'/'+parser.title+'.html', 'w')
        with closing(f):
            f.write(parser.content)

    def fetch_toc(self, host, path):
        print 'fetch toc ...'
        # html = fetchlib.fetch_html(host, path)
        html = fetchlib.Cache().get('html').decode('gbk').encode('utf-8')
        # print extract_body_inner_html(html)
        # parser = TianyaBookTocHTMLParser()
        parser = CurrentPageHrefHTMLParser()
        parser.feed(html)
        # parser.chapters_link = [path+x for x in parser.chapters_link]
        for x in parser.links:
            print x['title'], x['href']
        return parser

    def fetch_recursive(self, root, host, path):
        print 'start fetch recursive'
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
        print 'is_page', self.is_page(html)
        if self.is_page(html):
            self.fetch_save_page(root, host, path)
        else:
            self.fetch_save_chapter_small(root, host, path, html)

    def is_page(self, html):
        regex = re.compile('<pre>', re.IGNORECASE)
        return regex.search(html)

    def fetch_save_chapter_small(self, root, host, path, html):
        print 'fetch inner chapter ...'
        regex = re.compile(r'<font size=\+3>(.+?)</font>', re.IGNORECASE)
        m = regex.search(html)
        title = m.group(1)
        root = root + '/' + title
        if not os.path.exists(root):
            os.makedirs(root)

        print title

        regex = re.compile(r'<HR\b.+?<HR\b.*?>', re.IGNORECASE | re.DOTALL)
        m = regex.search(html)
        content = m.group(0)

        # save toc
        f = open(root+'/index.html', 'w')
        with closing(f):
            f.write(content)

        parser = TianyaBookInnerTocHTMLParser()
        parser.feed(html);
        baselink = os.path.dirname(path)
        chapters_link = [baselink+'/'+x for x in parser.chapters_link]
        print chapters_link
        for x in parser.chapters_title:
            self.fetch_save_page(root, host, path)

root = '../book/十日谈'
host = 'www.tianyabook.com'
    
xcfetch = XcFetch()
path = '/waiguo2005/b/bujiaqiu/srt/'
html = xcfetch.fetch_toc(host, path)
# html = xcfetch.fetch_save_page(root, host, path)
# xcfetch.fetch_recursive(root, host, path)
path = '/waiguo2005/b/bujiaqiu/srt/0001.htm'
# xcfetch.fetch_save_chapter(root, host, path)
path = '/waiguo2005/b/bujiaqiu/srt/1.html'
# html = fetchlib.fetch_html(host, path);
# html = fetchlib.Cache().get('html').decode('gbk').encode('utf-8')
# xcfetch.fetch_save_chapter_small(root, host, path, html)
