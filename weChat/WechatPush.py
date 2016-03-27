#!/usr/bin/env python
#-*- coding:utf-8 -*-
import urllib2,json
import datetime,time
from config import *
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
class WechatPush():
  def __init__(self,appid,secrect,file_name):
    # 传入appid
    self.appid = appid
    # 传入密码
    self.secrect = secrect
    # 传入记录token和过期时间的文件名
    self.file_name=file_name
  def build_timestamp(self,interval):
    # 传入时间间隔,得到指定interval后的时间 格式为"2015-07-01 14:41:40"
    now = datetime.datetime.now()
    delta = datetime.timedelta(seconds=interval)
    now_interval=now + delta
    return now_interval.strftime('%Y-%m-%d %H:%M:%S')
  def check_token_expires(self):
    # 判断token是否过期
    with open(self.file_name,'r') as f:
      line=f.read()
      if len(line)>0:
        expires_time=line.split(",")[1]
        token=line.split(",")[0]
      else:
        return "","true"
    curr_time=time.strftime('%Y-%m-%d %H:%M:%S')
    # 如果过期返回false
    if curr_time>expires_time:
      return token,"false"
    # 没过期返回true
    else:
      return token,"true"
  def getToken(self):
    # 获取accessToken
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='+self.appid + "&secret="+self.secrect
    try:
      f = urllib2.urlopen(url)
      s = f.read()
      # 读取json数据
      j = json.loads(s)
      j.keys()
      # 从json中获取token
      token = j['access_token']
      # 从json中获取过期时长
      expires_in =j['expires_in']
      # 将得到的过期时长减去300秒然后与当前时间做相加计算然后写入到过期文件
      write_expires=self.build_timestamp(int(expires_in-300))
      content="%s,%s" % (token,write_expires)
      with open(self.file_name,'w') as f:
        f.write(content)
    except Exception,e:
      print e
    return token
  def post_data(self,url,para_dct):
    """触发post请求微信发送最终的模板消息"""
    para_data = para_dct
    f = urllib2.urlopen(url,para_data)
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
if __name__ == "__main__":
  def alarm(title,hostname,timestap,level,message,state,tail):
    """报警函数"""
    color="#FF0000"
    data={"first":{"value":title},"keyword1":{"value":hostname,"color":color},"keyword2":{"value":timestap,"color":color},"keyword3":{"value":level,"color":color},"keyword4":{"value":message,"color":color},"keyword5":{"value":state,"color":color},"remark":{"value":tail}}
    return data
  def recover(title,message,alarm_time,recover_time,continue_time,tail):
    """恢复函数"""
    re_color="#228B22"
    data={"first":{"value":title},"content":{"value":message,"color":re_color},"occurtime":{"value":alarm_time,"color":re_color},"recovertime":{"value":recover_time,"color":re_color},"lasttime":{"value":continue_time,"color":re_color},"remark":{"value":tail}}
    return data
  # data=alarm("测试的报警消息","8.8.8.8",time.ctime(),"最高级别","然并卵","挂了","大傻路赶紧处理")
  # 实例化类
  webchart=WechatPush(appid,secrect,file_name)
  url="http://www.xiaoniu88.com"
  print len(sys.argv)
  # 发送报警消息
  if len(sys.argv) == 9:
    title=sys.argv[1]
    hostname=sys.argv[2]
    timestap=sys.argv[3]
    level=sys.argv[4]
    message=sys.argv[5]
    state=sys.argv[6]
    tail=sys.argv[7]
    print "sys.argv[1]"+sys.argv[1]
    print "sys.argv[2]"+sys.argv[2]
    print "sys.argv[3]"+sys.argv[3]
    print "sys.argv[4]"+sys.argv[4]
    print "sys.argv[5]"+sys.argv[5]
    print "sys.argv[6]"+sys.argv[6]
    print "sys.argv[7]"+sys.argv[7]
    print "sys.argv[8]"+sys.argv[8]
    with open("/etc/zabbix/moniter_scripts/test.log",'a+') as f:
      f.write(title+"\n")
      f.write(hostname+"\n")
      f.write(timestap+"\n")
      f.write(level+"\n")
      f.write(message+"\n")
      f.write(state+"\n")
      f.write(tail+"\n")
      f.write("%s_%s" % ("group",sys.argv[8])+"\n")
    data=alarm(title,hostname,timestap,level,message,state,tail)
    group_name="%s_%s" % ("group",sys.argv[8])
    for touser in eval("%s_%s" % ("group",sys.argv[8])):
        webchart.do_push(touser,alarm_id,url,"",data)
    for touser in group_super:
        webchart.do_push(touser,alarm_id,url,"",data)
  #发送恢复消息
  elif len(sys.argv) == 8:
    title=sys.argv[1]
    message=sys.argv[2]
    alarm_time=sys.argv[3]
    recover_time=sys.argv[4]
    continue_time=sys.argv[5]
    tail=sys.argv[6]
    print "sys.argv[1]"+sys.argv[1]
    print "sys.argv[2]"+sys.argv[2]
    print "sys.argv[3]"+sys.argv[3]
    print "sys.argv[4]"+sys.argv[4]
    print "sys.argv[5]"+sys.argv[5]
    print "sys.argv[6]"+sys.argv[6]
    print "sys.argv[7]"+sys.argv[7]
    data=recover(title,message,alarm_time,recover_time,continue_time,tail)
    for touser in eval("%s_%s" % ("group",sys.argv[7])):
      webchart.do_push(touser,recover_id,url,"",data)
    for touser in group_super:
      webchart.do_push(touser,recover_id,url,"",data)