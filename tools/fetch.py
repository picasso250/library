#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, time, thread, glib, gobject, datetime
import pickle, re
import pygst
pygst.require("0.10")
import gst, json, urllib, httplib, contextlib, random, binascii
from select import select
from Cookie import SimpleCookie
from contextlib import closing 

from HTMLParser import HTMLParser

# create a subclass and override the handler methods
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
            content = [ '<p>' + re.sub(r'\r\n', '', x) + '</p>' for x in content]
            content = '\n'.join(content)
            self.content = content
        if self.last_tag == 'title' and self.title is None:
            data = re.split('---', data)
            self.title = data[0]

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

class XcFetch(object):
    def fetch_html(self, host, path):
        cache = Cache()
        data = {
                }
        data = urllib.urlencode(data)

        print 'fetch ...'
        with closing(httplib.HTTPConnection(host)) as conn:
            headers = self.get_headers_for_request()
            conn.request("GET", path, data, headers)
            response = conn.getresponse()

            body = response.read();
            cache.set('html', body)
        return body.decode('gb2312').encode('utf-8')

    def get_headers_for_request(self, extra = {}):
        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/28.0.1500.71 Chrome/28.0.1500.71 Safari/537.36',
            'Referer': 'http://douban.fm/',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        return headers

    def fetch_save_page(self, root, host, path):
        html = self.fetch_html(host, path)
        # html = Cache().get('html').decode('gb2312').encode('utf-8')
        parser = TianyaBookContentHTMLParser()
        parser.feed(html)

        f = open(root+'/'+parser.title+'.html', 'w')
        with closing(f):
            f.write(parser.content)

    def fetch_toc(self, host, path):
        # html = self.fetch_html(host, path)
        html = Cache().get('html').decode('gb2312').encode('utf-8')
        parser = TianyaBookTocHTMLParser()
        parser.feed(html)
        parser.chapters_link = [path+x for x in parser.chapters_link]
        return parser

    def fetch_recursive(self, root, host, path):
        parser = self.fetch_toc(host, path)
        self.save_toc(root, parser.chapters_title)

        for x in parser.chapters_link:
            print x
            self.fetch_save_page(root, host, x)

    def save_toc(self, root, titles):
        chapters = ['<a href="'+x+'">'+x+'</a>' for x in titles]
        f = open(root+'/index.html', 'w')
        with closing(f):
            f.write('\n'.join(chapters))

class Cache:
    """docstring for cache"""
    def has(self, name):
        file_name = self.get_cache_file_name(name)
        return os.path.exists(file_name)

    def get(self, name, default = None):
        file_name = self.get_cache_file_name(name)
        if not os.path.exists(file_name):
            return default
        cache_file = open(file_name, 'rb')
        content = pickle.load(cache_file)
        cache_file.close()
        return content

    def set(self, name, content):
        file_name = self.get_cache_file_name(name)
        cache_file = open(file_name, 'wb')
        pickle.dump(content, cache_file)
        cache_file.close()

    def get_cache_file_name(self, name):
        # file should put to /tmp ?
        # but maybe someone clear their /tmp everyday ?
        return name + '.cache'


root = '../book/十日谈'
host = 'www.tianyabook.com'
path = '/waiguo2005/b/bujiaqiu/srt/001.htm'
    
xcfetch = XcFetch()
path = '/waiguo2005/b/bujiaqiu/srt/'
# html = xcfetch.fetch_toc(host, path)
# html = xcfetch.fetch_save_page(root, host, path)
xcfetch.fetch_recursive(root, host, path)