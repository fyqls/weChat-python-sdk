# -*- coding: utf-8 -*-
from datetime import datetime

__author__ = 'Vincent Ting'

import cookielib
import urllib2
import urllib
import json
import poster
import hashlib
import time
import re


class BaseClient(object):
    def __init__(self, appid=None, appsecret=None, file_name='/tmp/weixin.krb'):

        if not appid or not appsecret:
            raise ValueError

        self.appid = appid
        self.appsecret = appsecret
        self.file_name = file_name

    def build_timestamp(self, interval):
        # 传入时间间隔,得到指定interval后的时间 格式为"2015-07-01 14:41:40"
        now = datetime.datetime.now()
        delta = datetime.timedelta(seconds=interval)
        now_interval = now + delta
        return now_interval.strftime('%Y-%m-%d %H:%M:%S')

    def check_token_expires(self):
        # 判断token是否过期
        with open(self.file_name, 'r') as f:
            line = f.read()
            if len(line) > 0:
                expires_time = line.split(",")[1]
                token = line.split(",")[0]
            else:
                return "", "true"
        curr_time = time.strftime('%Y-%m-%d %H:%M:%S')
        # 如果过期返回false
        if curr_time > expires_time:
            return token, "false"
        # 没过期返回true
        else:
            return token, "true"

    def getToken(self):
        # 获取accessToken
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + self.appid + "&secret=" + self.appsecret
        try:
            f = urllib2.urlopen(url)
            s = f.read()
            # 读取json数据
            j = json.loads(s)
            j.keys()
            # 从json中获取token
            token = j['access_token']
            # 从json中获取过期时长
            expires_in = j['expires_in']
            # 将得到的过期时长减去300秒然后与当前时间做相加计算然后写入到过期文件
            write_expires = self.build_timestamp(int(expires_in - 300))
            content = "%s,%s" % (token, write_expires)
            with open(self.file_name, 'w') as f:
                f.write(content)
        except Exception, e:
            print e
        return token

    def post_data(self, url, para_dct):
        """触发post请求微信发送最终的模板消息"""
        para_data = para_dct
        f = urllib2.urlopen(url, para_data)
        content = f.read()
        return content

    def do_push(self,touser,template_id,url,topcolor,data):
        '''推送消息 '''
        #获取存入到过期文件中的token,同时判断是否过期
        token,if_token_expires=self.check_token_expires()
        #如果过期了就重新获取token
        if if_token_expires=="false":
          token=self.getToken()
        # 背景色设置,貌似不生效
        if topcolor.strip()=='':
          topcolor = "#7B68EE"
        #最红post的求情数据
        dict_arr = {'touser': touser, 'template_id':template_id, 'url':url, 'topcolor':topcolor,'data':data}
        json_template = json.dumps(dict_arr)
        requst_url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token="+token
        content = self.post_data(requst_url,json_template)
        #读取json数据
        j = json.loads(content)
        j.keys()
        errcode = j['errcode']
        errmsg = j['errmsg']
        #print errmsg

    # def __init__(self, appid=None, appsecret=None, finename='/tmp/weixin.krb'):
    #     """
    #     登录公共平台服务器，如果失败将报客户端登录异常错误
    #     :param email:
    #     :param password:
    #     :raise:
    #     """
    #     if not appid or not appsecret:
    #         raise ValueError
    #     self.setOpener()
    #
    #     url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='+appid + "&secret="+appsecret
    #     try:
    #         f = urllib2.urlopen(url)
    #         s = f.read()
    #         # 读取json数据
    #         j = json.loads(s)
    #         j.keys()
    #         # 从json中获取token
    #         self.token = j['access_token']
    #     except BaseException,e:
    #         raise ClientLoginException(e)
    #     time.sleep(1)

    def setOpener(self):
        """
        设置请求头部信息模拟浏览器
        """
        self.opener = poster.streaminghttp.register_openers()
        self.opener.add_handler(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        self.opener.addheaders = [('Accept', 'application/json, text/javascript, */*; q=0.01'),
                                  ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
                                  ('Referer', 'https://mp.weixin.qq.com/'),
                                  ('Cache-Control', 'max-age=0'),
                                  ('Connection', 'keep-alive'),
                                  ('Host', 'mp.weixin.qq.com'),
                                  ('Origin', 'mp.weixin.qq.com'),
                                  ('X-Requested-With', 'XMLHttpRequest'),
                                  ('User-Agent',
                                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36')]

    def _sendMsg(self, sendTo, data):
        """
        基础发送信息的方法
        :param sendTo:
        :param data:
        :return:
        """
        if type(sendTo) == type([]):
            for _sendTo in sendTo:
                self._sendMsg(_sendTo, data)
            return

        self.opener.addheaders += [('Referer', 'http://mp.weixin.qq.com/cgi-bin/singlemsgpage?fromfakeid={0}'
                                               '&msgid=&source=&count=20&t=wxm-singlechat&lang=zh_CN'.format(sendTo))]
        body = {
            'error': 'false',
            'token': self.token,
            'tofakeid': sendTo,
            'ajax': 1}
        body.update(data)
        try:
            msg = json.loads(self.opener.open("https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&"
                                              "lang=zh_CN", urllib.urlencode(body), timeout=5).read())['msg']
        except urllib2.URLError:
            time.sleep(1)
            return self._sendMsg(sendTo, data)
        print msg
        time.sleep(1)
        return msg

    def _uploadImg(self, img):
        """
        根据图片地址来上传图片，返回上传结果id
        :param img:
        :return:
        """
        params = {'uploadfile': open(img, "rb")}
        data, headers = poster.encode.multipart_encode(params)
        request = urllib2.Request('http://mp.weixin.qq.com/cgi-bin/uploadmaterial?'
                                  'cgi=uploadmaterial&type=2&token={0}&t=iframe-uploadfile&'
                                  'lang=zh_CN&formId=file_from_{1}000'.format(self.token, int(time.time())),
                                  data, headers)
        result = urllib2.urlopen(request)
        find_id = re.compile("\d+")
        time.sleep(1)
        return find_id.findall(result.read())[-1]

    def _delImg(self, file_id):
        """
        根据图片ID来删除图片
        :param file_id:
        """
        self.opener.open('http://mp.weixin.qq.com/cgi-bin/modifyfile?oper=del&lang=zh_CN&t=ajax-response',
                         urllib.urlencode({'fileid': file_id,
                                           'token': self.token,
                                           'ajax': 1}))
        time.sleep(1)

    def _addAppMsg(self, title, content, file_id, digest='', sourceurl=''):
        """
        上传图文消息
        :param title:
        :param content:
        :param file_id:
        :param digest:
        :param sourceurl:
        :return:
        """
        msg = json.loads(self.opener.open(
            'http://mp.weixin.qq.com/cgi-bin/operate_appmsg?token={0}&lang=zh_CN&t=ajax-response&sub=create'.format(
                self.token),
            urllib.urlencode({'error': 'false',
                              'count': 1,
                              'AppMsgId': '',
                              'title0': title,
                              'digest0': digest,
                              'content0': content,
                              'fileid0': file_id,
                              'sourceurl0': sourceurl,
                              'token': self.token,
                              'ajax': 1})).read())
        time.sleep(1)
        return msg['msg'] == 'OK'

    def _getAppMsgId(self):
        """
        获取最新上传id
        :return:
        """
        msg = json.loads(self.opener.open(
            'http://mp.weixin.qq.com/cgi-bin/operate_appmsg?token={0}&lang=zh_CN&sub=list&t=ajax-appmsgs-fileselect&type=10&pageIdx=0&pagesize=10&formid=file_from_{1}000&subtype=3'.format(
                self.token, int(time.time())),
            urllib.urlencode({'token': self.token,
                              'ajax': 1})).read())
        time.sleep(1)
        return msg['List'][0]['appId']

    def _delAppMsg(self, app_msg_id):
        """
        根据id删除图文
        :param app_msg_id:
        """
        print self.opener.open('http://mp.weixin.qq.com/cgi-bin/operate_appmsg?sub=del&t=ajax-response',
                               urllib.urlencode({'AppMsgId': app_msg_id,
                                                 'token': self.token,
                                                 'ajax': 1})).read()
        time.sleep(1)


class ClientLoginException(Exception):
    pass
