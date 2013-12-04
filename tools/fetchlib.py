# -*- coding: utf-8 -*-

import sys, os, time, thread, datetime
import pickle, re
import urllib, httplib, contextlib, random
from Cookie import SimpleCookie
from contextlib import closing 

# fetch for one page
def fetch_html(host, path):
    cache = Cache()
    data = {}
    data = urllib.urlencode(data)

    print 'fetch', path, '...'
    with closing(httplib.HTTPConnection(host)) as conn:
        headers = get_headers_for_request()
        conn.request("GET", path, data, headers)
        response = conn.getresponse()
        body = response.read();
        cache.set('html', body)
    return body.decode('gbk').encode('utf-8')

# simulate chrome ua
def get_headers_for_request( extra = {}):
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/28.0.1500.71 Chrome/28.0.1500.71 Safari/537.36',
        'Referer': 'http://douban.fm/',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    return headers

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
