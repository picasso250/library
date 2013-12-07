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
    regex = re.compile(r'<body\b.+?>(.+)</?body>', re.IGNORECASE | re.DOTALL)
    match = regex.search(html)
    if match is None:
        print html
        print 'not good format to extract body'
        return ''
    return match.group(1)

def file_put_contents(filename, data):
    print 'save file', filename
    f = open(filename, 'w')
    with closing(f):
        f.write(data)

class XcFetch(object):
    def __init__(self):
        self.walked = []

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

    def fetch_recursive(self, root, host, path):
        if path in self.walked:
            print 'fetched', path, 'skip'
            return

        # fetch
        html = fetchlib.fetch_html(host, path)
        html = fetchlib.Cache().get('html').decode('gbk').encode('utf-8')

        # name
        name = os.path.basename(path)
        if len(name) == 0:
            name = 'index.html'

        if self.is_page(html):
            parser = TianyaBookContentHTMLParser()
            parser.feed(html)
            if parser.content is None:
                print html
                print 'content is None'
                return

            inner = '<h1>' + parser.title + '</h1>\n' + parser.content
            file_put_contents(root+'/'+name, inner)
            return
        else:
            inner = extract_body_inner_html(html)

        file_put_contents(root+'/'+name, inner)

        parser = CurrentPageHrefHTMLParser()
        parser.feed(html)
        basepath = os.path.dirname(path)
        for x in parser.links:
            href = x['href']
            if not ( href == 'index.html' or href == 'index.htm' ):
                print x['title'],
                self.fetch_recursive(root, host, basepath + '/' + href)

    def is_page(self, html):
        regex = re.compile('<pre>', re.IGNORECASE)
        return regex.search(html)


root = '../book/十日谈'
host = 'www.tianyabook.com'
    
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
