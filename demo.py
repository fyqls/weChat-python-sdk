# coding=utf-8
"""
首先需要在微信公共平台申请帐号 mp.weixin.qq.com
之后才可以使用下事例
"""
__author__ = 'lisong QIU'

from weChat.client import Client

client = Client(appid='wxfd7414fc987df416', appsecret='a7e2632b2dc9f5496520c2fc2b21e9c2')

#demo  推送文字信息,其中sendto为关注该帐号的某用户的fakeId

#client.sendTextMsg('xxxxxxx', 'Hello world')

client.do_push("","https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token=ACCESS_TOKEN")

#demo  推送图片信息,其中sendto为关注该帐号的某用户的fakeId，img为图片的文件路径

#client.sendImgMsg('xxxxxxx', './demo.png')
