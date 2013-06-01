#coding: u8

import urllib2
import urllib
import cookielib


class Net(object):
    def __init__(self):
        self.cookie = cookielib.LWPCookieJar()
        proxyhandler = urllib2.ProxyHandler({
            'https': 'http://127.0.0.1:8087',
            'http': 'http://127.0.0.1:8087'
        })
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cookie),
            #proxyhandler
        )
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.22 (KHTML, like Gecko) Ubuntu Chromium/25.0.1',
            'Accept-Charset': 'GBK,utf-8',
        }
        urllib2.install_opener(self.opener)

    def post(self, url, params):
        if isinstance(params, dict):
            params = urllib.urlencode(params)
        return self.opener.open(urllib2.Request(url, params, self.headers), timeout=120).read()

    def get(self, url):
        return self.opener.open(urllib2.Request(url, headers=self.headers), timeout=120).read()

    def get_cookie(self, name):
        for cookie in self.cookie:
            if cookie.name == name:
                return cookie.value
