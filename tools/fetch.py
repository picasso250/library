#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, time, thread, glib, gobject, datetime
import pickle
import pygst
pygst.require("0.10")
import gst, json, urllib, httplib, contextlib, random, binascii
from select import select
from Cookie import SimpleCookie
from contextlib import closing 

from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class TianyaHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.last_tag = None
    def handle_starttag(self, tag, attrs):
        self.last_tag = tag
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        if self.last_tag == 'pre':
            self.content = data

class XcFetch(object):
    def fetch_html(self):
        cache = Cache()
        data = {
                }
        data = urllib.urlencode(data)

        print 'fetch ...'
        with closing(self.get_conn()) as conn:
            headers = self.get_headers_for_request()
            conn.request("GET", "/waiguo2005/b/bujiaqiu/srt/001.htm", data, headers)
            response = conn.getresponse()

            body = response.read();
            cache.set('html', body)
        return body.decode('gb2312').encode('utf-8')

    def get_conn(self):
        return httplib.HTTPConnection("www.tianyabook.com")


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

    def fetch_content(self):
        xcfetch = XcFetch()
        # html = xcfetch.fetch_html()
        html = Cache().get('html').decode('gb2312').encode('utf-8')

        # instantiate the parser and fed it some HTML
        parser = TianyaHTMLParser()
        parser.feed(html)
        return parser.content



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


        
xcfetch = XcFetch()
content = xcfetch.fetch_content()
print content
