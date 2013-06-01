#coding: u8

import json
import logging
import random
import time
import thread
from itertools import count

import net
import xiaoi


r = lambda: random.random()
t = lambda: time.time()
# 本方发送消息的id防止重复发送
tick = count(int(r() * 999999) + 12345678)

n = net.Net()


class Coco(object):
    UPDATE_STATUS = 0x01
    MESSAGE = 0x02
    FORCE_OFFLINE = 0x03
    # 只有带有SYM前缀的消息才会作出响应
    SYM = '#'

    def __init__(self, status='online'):
        self.status = status
        self.clientid = int((r() * 89999999)) + 10000000
        # 有时候可能会收到相同的消息，通过对方传来的msg_id可以判断
        # 如果已经在msg_ids中那么就丢弃此消息
        self.msg_ids = set()
        # 心跳次数
        self.tip_id = int(r() * 999999)
        # 缓存所有信息
        self.group_cache = {}
        self.stopped = False
        self.t1 = time.time()

    def login(self, qq, pwd, vc=None):
        '''登录'''
        self.qq = qq
        self.pwd = pwd
        if vc is not None:
            # 如果给定了验证码则是用户已经输入了验证码才会进入此if语句
            self.vc = vc
            state = '0'
        else:
            # 检查是否需要验证码
            url = 'https://ssl.ptlogin2.qq.com/check?uin={0}&appid=1003903&r={1}'
            url = url.format(self.qq, r())
            logging.debug('checking verifycode...')
            state, vc, uin = self.jsonp2list(n.get(url))
            self.uin = self._hex2chr(uin.replace('\\x', ''))
            self.vc = vc
        if state == '0':
            logging.debug('no need verifycode.')
            return {'need_verify_code': False, 'msg': self._login()}
        if state == '1':
            # 要验证码
            logging.debug('need verifycode!')
            return {'need_verify_code': True, 'data': self._get_verifycode()}

    def _login(self):
        logging.debug('logining...')
        self._encode_pwd()
        url = 'http://ptlogin2.qq.com/login?u={0}&p={1}&verifycode={2}&webqq_type=40&remember_uin=1&login2qq=1&aid=1003903&u1=http%3A%2F%2Fweb.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D40&h=1&ptredirect=0&ptlang=2052&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=4-3-2475914&mibao_css=m_webqq&t=1&g=1'
        url = url.format(self.qq, self.encoded_pwd, self.vc.upper())
        jsn = self.jsonp2list(n.get(url))
        msg = unicode(jsn[4], 'u8')
        if u'登录成功' in msg:
            logging.debug('login success.')
            self._get_psession_id(self.status)
            self.nick = unicode(jsn[5], 'u8')
            logging.debug(u'nick: {0}.'.format(self.nick))
        else:
            logging.debug('login fail!')
            logging.debug(u'error msg: {0}.'.format(msg))
            return msg

    def poll(self):
        if not hasattr(self, 'psessionid'):
            return
        logging.debug('polling...')
        n.headers.update({
            'Referer': 'https://d.web2.qq.com/proxy.html?v=20110412001&callback=1&id=3'
        })
        url = 'http://d.web2.qq.com/channel/poll2'
        r = {
            'key': 0,
            'ids': [],
            'clientid': self.clientid,
            'psessionid': self.psessionid}
        r = json.dumps(r)
        jsn = n.post(url, {'r': r, 'clientid': self.clientid, 'psessionid': self.psessionid})
        res = json.loads(jsn)
        retcode = res['retcode']
        if retcode == 0:
            for i in res['result']:
                poll_type = i['poll_type']
                value = i['value']
                if poll_type in ('group_message', 'message'):
                    msg_id = value['msg_id']
                    if msg_id not in self.msg_ids:
                        self.msg_ids.add(msg_id)
                        thread.start_new_thread(self.robot, (value,))

    def send_msg_to_friend(self, uin, msg):
        '''发送消息给好友'''
        if isinstance(msg, unicode):
            msg = msg.encode('u8')
        msg = msg.replace('"', '\\"').replace('\r\n', '\\n')
        font = {
            'name': '微软雅黑',
            'size': '10',
            'style': [0, 0, 0],
            'color': '000000'
        }
        name = font['name']
        if isinstance(name, unicode):
            font['name'] = name.encode('u8')
        url = 'http://d.web2.qq.com/channel/send_buddy_msg2'
        n.headers.update({
            'Referer': 'https://d.web2.qq.com/proxy.html?v=20110412001&callback=1&id=3'
        })
        style = ','.join(map(str, font['style']))
        msg = '["' + msg + '",["font",{"name":"' + name + '","size":"' + \
              font['size'] + '","style":[' + style + '],"color":"' + \
              font['color'] + '"}]]'
        r = {
            'to': uin,
            'face': 0,
            'msg_id': tick.next(),
            'content': msg,
            'clientid': self.clientid,
            'psessionid': self.psessionid
        }
        jsn = n.post(url, {
            'r': json.dumps(r),
            'clientid': self.clientid,
            'psessionid': self.psessionid
        })
        return json.loads(jsn)

    def robot(self, value):
        group = 'group_code' in value
        msg = self.analyze_msg(value['content']).strip()
        if group:
            if not msg.startswith(self.SYM):
                return
            msg = msg[len(self.SYM):]
        print 'IN: ', msg
        if self.stopped:
            return
        msg = xiaoi.xiaoi(msg)
        if 'http://www.xiaoi.com' in msg:
            msg = u'我开玩笑的……'
        msg = msg.replace(u'小i', u'Robot').strip()
        if msg:
            print 'OUT: ', msg
            if group:
                group_code = value['group_code']
                gid = self.group_cache[group_code]['gid']
                self.send_msg(gid, msg)
            else:
                self.send_msg_to_friend(value['from_uin'], msg)

    def analyze_msg(self, content):
        '''解析msg, 只取里面的字符串'''
        msg = []
        for i in content:
            if isinstance(i, unicode):
                msg.append(i)
        return ''.join(msg)

    def _encode_pwd(self):
        from hashlib import md5 as _md5
        md5 = lambda x: _md5(x).hexdigest().upper()
        self.encoded_pwd = md5(
            md5(self._hex2chr(md5(self.pwd)) + self.uin) + self.vc.upper())

    def _get_psession_id(self, status):
        logging.debug('getting psessionid...')
        # 获取两个cookie的值
        self.skey = n.get_cookie('skey')
        self.ptwebqq = n.get_cookie('ptwebqq')
        r = {
            'status': status,
            'ptwebqq': self.ptwebqq,
            'passwd_sig': '',
            'clientid': self.clientid,
            'psessionid': 'null'}
        r = json.dumps(r)
        url = 'https://d.web2.qq.com/channel/login2'
        # Referer很重要，不然会返回103
        n.headers.update({
            'Referer': 'https://d.web2.qq.com/proxy.html?v=20110412001&callback=1&id=3'
        })
        jsn = n.post(url, {'r': r, 'clientid': self.clientid, 'psessionid': 'null'})
        result = json.loads(jsn)['result']
        self.vfwebqq = result['vfwebqq']
        self.psessionid = result['psessionid']
        self.status = result['status']
        logging.debug('psessionid gotten.')

    def _hash2(self):
        '''新的hash算法http://0.web.qstatic.com/webqqpic/pubapps/0/50/eqq.all.js?t=20130417001第596行'''
        b = self.qq
        i = self.ptwebqq
        a = i + 'password error'
        s = ''
        j = []
        while 1:
            if len(s) <= len(a):
                s += b
                if len(s) == len(a):
                    break
            else:
                s = s[:len(a)]
                break
        for d in range(len(s)):
            j.append(ord(s[d]) ^ ord(a[d]))

        import string
        a = list(string.digits) + ['A', 'B', 'C', 'D', 'E', 'F']
        s = ''
        for d in j:
            s += a[d >> 4 & 15]
            s += a[d & 15]
        return s

    def get_my_group_info(self):
        '''得到群组信息'''
        url = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
        n.headers.update({
            'Referer': 'https://d.web2.qq.com/proxy.html?v=20110412001&callback=1&id=3'
        })
        jsn = n.post(url, {'r': json.dumps({'vfwebqq': self.vfwebqq})})
        result = json.loads(jsn)['result']
        marks = {}
        for i in result['gmarklist']:
            marks[i['uin']] = i['markname']
        for i in result['gnamelist']:
            gid = i['gid']
            code = i.pop('code')
            i.pop('flag')
            i['name'] = marks.get(gid, i['name'])
            self.group_cache[code] = i

    def send_msg(self, gid, msg):
        '''发送消息'''
        if isinstance(msg, unicode):
            msg = msg.encode('u8')
        msg = msg.replace('"', '\\"').replace('\r\n', '\\n')
        font = {
            'name': '微软雅黑',
            'size': '10',
            'style': [0, 0, 0],
            'color': '000000'
        }
        name = font['name']
        if isinstance(name, unicode):
            font['name'] = name.encode('u8')
        url = 'http://d.web2.qq.com/channel/send_qun_msg2'
        n.headers.update({
            'Referer': 'http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=3'
        })
        style = ','.join(map(str, font['style']))
        msg = '["' + msg + '",["font",{"name":"' + name + '","size":"' + \
              font['size'] + '","style":[' + style + '],"color":"' + \
              font['color'] + '"}]]'
        r = {
            'group_uin': gid,
            'msg_id': tick.next(),
            'content': msg,
            'clientid': self.clientid,
            'psessionid': self.psessionid
        }
        jsn = n.post(url, {
            'r': json.dumps(r),
            'clientid': self.clientid,
            'psessionid': self.psessionid
        })
        return json.loads(jsn)

    def get_msg_tip(self):
        '''心跳，不过好像用poll了，这个没什么用？'''
        import time
        while 1:
            time.sleep(60)
            try:
                url = 'http://web.qq.com/web2/get_msg_tip?uin=&tp=1&id=0&retype=1&rc=%s&lv=3&t=%s'
                url %= self.tip_id, t()
                yield json.loads(n.get(url))
                self.tip_id += 1
            except:
                pass

    def _get_verifycode(self):
        '''获取验证码'''
        url = 'http://captcha.qq.com/getimage?aid=1003903&r=%s&uin=%s&vc_type=%s'
        url %= r(), self.qq, self.vc
        logging.debug('getting verifycode')
        img = n.get(url)
        open('vc.jpg', 'wb').write(img)
        return img

    def _hex2chr(self, s):
        return ''.join([chr(int(''.join(h), 16)) for h in self.group(s, 2)])

    @staticmethod
    def group(seq, size):
        def take(seq, n):
            for i in xrange(n):
                yield seq.next()

        if not hasattr(seq, 'next'):
            seq = iter(seq)
        while True:
            x = list(take(seq, size))
            if x:
                yield x
            else:
                break

    @staticmethod
    def jsonp2list(jsonp):
        args = jsonp[jsonp.find('(') + 1: jsonp.rfind(')')]
        return [i.strip("' ") for i in args.split(',')]


def test():
    coco = Coco()
    qq = '12345678'
    pwd = '12345678'
    fail = coco.login(qq, pwd)
    if not fail['need_verify_code']:
        if fail['msg'] is not None:
            print fail
            return
    else:
        vc = raw_input('verify code:')
        coco.login(qq, pwd, vc)
    # 跟踪哪些群组
    # 得到群组信息(主面板)
    coco.get_my_group_info()
    print coco.group_cache
    while 1:
        time.sleep(.5)
        coco.poll()


if __name__ == '__main__':
    test()
