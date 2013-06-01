# coding: u8

import requests
from pyquery import PyQuery

import verify


__all__ = ['xiaoi']


home_page = 'http://nlp.xiaoi.com/robot/demo/wap/wap-demo.action'
qa_page = 'http://nlp.xiaoi.com/robot/demo/wap/wap-demo.action'
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3',
}


def xiaoi(msg):
    r = requests.get(url=home_page, headers=headers)
    cookies = verify.sig(r.cookies)
    params = {'requestContent': msg}
    r = requests.post(
        url=qa_page, cookies=cookies, headers=headers, params=params)
    jQuery = PyQuery(r.text.encode('u8'))
    return jQuery('.wap_cn2').text()[7:]


if __name__ == '__main__':
    print xiaoi('你是哪个')
    print xiaoi('你家在哪里')
    print xiaoi('你几岁了')
    print xiaoi('讲个笑话吧')
    print xiaoi('南京天气')
    print xiaoi('几点了')
    print xiaoi('中国美国多远')
    print xiaoi('你弱爆了')
    print xiaoi('1 + 1 = 3')
    print xiaoi('你妹')
