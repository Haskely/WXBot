# -*- coding: utf-8 -*-
# !/usr/bin/env python

import emoji
import threading
import codecs
import qrcode
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import http.cookiejar
import requests
import xml.dom.minidom
import json
import time
import re
import sys
import os
import subprocess
import random
import multiprocessing
import platform
import logging
import http.client
from collections import defaultdict
from urllib.parse import urlparse
from lxml import html
from colorama import init, Fore, Back, Style
import mimetypes
from requests_toolbelt.multipart.encoder import MultipartEncoder

init(autoreset=True)

def _trans_emoji(text):
    while True:
        left = text.find("<span class=\"emoji emoji")
        if left != -1:
            right = text[left:].find("\"></span>") + left
            text = text[:left] + (r"\U000" + text[left + 24:right]).encode().decode("unicode-escape","replace") + text[right + 9:]
        else:
            break
    return text


def _formate_Name(name):
    # '<span class="emoji emoji1f338"></span>'
    name = _trans_emoji(name)
    return name


def _format_text( text):
    text = _trans_emoji(text)
    return text


def catchKeyboardInterrupt(fn):
    def wrapper(*args):
        try:
            return fn(*args)
        except KeyboardInterrupt:
            print('\n[*] 强制退出程序')
            logging.debug('[*] 强制退出程序')

    return wrapper


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, str):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.items():
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(value, str):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv


def _reaction_Msg1(self,dic,msg,loc):

    self.isAuthorized = False

    if msg["FromUserName"] == self.User["UserName"]:
        self.isAuthorized = True
        replycommand_dst_id = dic['dst_id']
    else:
        if dic['isGroup']:
            replycommand_dst_id = dic['group_id']
        else:
            replycommand_dst_id = dic['src_id']

    if dic['srcName'] in self.Administraters:
        self.isAuthorized = True

    if dic['con'][:3] == "指令！":
        if self.isAuthorized:
            self.commandmode[replycommand_dst_id] = time.time()
            self.webwxsendmsg("指令模式已开启", replycommand_dst_id)
        else:
            self.webwxsendmsg("别费劲了，我只听主人的[微笑]", replycommand_dst_id)

    if replycommand_dst_id in self.commandmode and self.isAuthorized:
        isCommand = True
        
        if dic['con'] == "指令！":
            rep = (u"可用指令有:\n"
                   "\t'群白名单'\n"
                   "\t'把“什么”加到群白名单'\n"
                   "\t'把“什么”移出群白名单'\n"
                   "\t'黑名单'\n"
                   "\t'把@谁 加到黑名单'\n"
                   "\t'把@谁 移出黑名单'\n"
                   "\t'开启自动回复模式'\n"
                   "\t'关闭自动回复模式'\n"
                   "\t'机器人安静'\n"
                   "\t'机器人自由'\n"
                   "\t'开启撤回终结者模式'\n"
                   "\t'关闭撤回终结者模式'\n"
                   "\t'状态'\n"
                   + '\U0001f338')
            self.webwxsendmsg(rep, replycommand_dst_id)

        elif "管理员名单" in dic['con']:
            if "加到管理员名单" in dic['con']:
                if "把这个人加到管理员名单" in dic['con']:
                    name = dic['dstName']
                else:
                    name = dic['con'][ dic['con'].find("把@") + 2: dic['con'].rfind("加到管理员名单")][:-1]
                self.Administraters.add(name)
                self.webwxsendmsg("System:好的，已成功把" + name + "加到管理员名单[机智]", replycommand_dst_id)
                self.save_list("管理员名单.txt", self.Administraters)
            elif "移出管理员名单" in dic['con']:
                if "把这个人移出管理员名单" in dic['con']:
                    name = dic['dstName']
                else:
                    name = dic['con'][ dic['con'].find("把@") + 2: dic['con'].rfind("移出管理员名单")][:-1]

                if name in self.Administraters:
                    self.Administraters.remove(name)
                    self.webwxsendmsg("System:遵命主人！已成功把" + name + "移出管理员名单[玫瑰]", replycommand_dst_id)
                    self.save_list("管理员名单.txt", self.Administraters)
                else:
                    self.webwxsendmsg("System:主人~" + name + "本来就不在管理员名单啊[发呆]", replycommand_dst_id)
            else:
                self.webwxsendmsg("System:当前在管理员名单的人有:%s" % "、".join(self.Administraters), replycommand_dst_id)

        elif "群白名单" in dic['con']:
            if "加到群白名单" in dic['con']:
                if "把这个群加到群白名单" in dic['con']:
                    groupname = self.getGroupName(replycommand_dst_id)
                else:
                    groupname = dic['con'][ dic['con'].find("把“") + 2: dic['con'].rfind("”加到群白名单")]
                self.avalible_group_dst.add(groupname)
                self.webwxsendmsg("System:好的，已成功把“" + groupname + "”加到群白名单[奸笑]", replycommand_dst_id)
                self.save_list("群白名单.txt", self.avalible_group_dst)
            elif "移出群白名单" in dic['con']:
                if "把这个群移出群白名单" in dic['con']:
                    groupname = self.getGroupName(replycommand_dst_id)
                else:
                    groupname = dic['con'][ dic['con'].find("把“") + 2: dic['con'].rfind("”移出群白名单")]
                if groupname in self.avalible_group_dst:
                    self.avalible_group_dst.remove(groupname)
                    self.webwxsendmsg("System:遵命主人！已成功把“" + groupname + "”移出群白名单[吓]", replycommand_dst_id)
                    self.save_list("群白名单.txt", self.avalible_group_dst)
                else:
                    self.webwxsendmsg("System:主人~" + groupname + "本来就不在群白名单啊[尴尬]", replycommand_dst_id)
            else:
                self.webwxsendmsg("System:当前在白名单的群有:%s" % "、".join(self.avalible_group_dst), replycommand_dst_id)
        elif "黑名单" in dic['con']:
            if "加到黑名单" in dic['con']:
                if "把这个人加到黑名单" in dic['con']:
                    name = dic['dstName']
                else:
                    name = dic['con'][ dic['con'].find("把@") + 2: dic['con'].rfind("加到黑名单")][:-1]
                self.black_contact_dst.add(name)
                self.webwxsendmsg("System:好的，已成功把" + name + "加到黑名单[微笑]", replycommand_dst_id)
                self.save_list("黑名单.txt", self.black_contact_dst)
            elif "移出黑名单" in dic['con']:
                if "把这个人移出黑名单" in dic['con']:
                    name = dic['dstName']
                else:
                    name = dic['con'][ dic['con'].find("把@") + 2: dic['con'].rfind("移出黑名单")][:-1]
                if name in self.black_contact_dst:
                    self.black_contact_dst.remove(name)
                    self.webwxsendmsg("System:遵命主人！已成功把" + name + "移出黑名单[玫瑰]", replycommand_dst_id)
                    self.save_list("黑名单.txt", self.black_contact_dst)
                else:
                    self.webwxsendmsg("System:主人~" + name + "本来就不在黑名单啊[发呆]", replycommand_dst_id)
            else:
                self.webwxsendmsg("System:当前在黑名单的人有:%s" % "、".join(self.black_contact_dst), replycommand_dst_id)
        elif "自动回复模式" in dic['con']:
            if "开启自动回复模式" in dic['con']:
                self.autoReplyMode = True
                self.webwxsendmsg("[微信机器人]:我来啦！[嘿哈]", replycommand_dst_id)
                self.robotready[replycommand_dst_id] = time.time()
            elif "关闭自动回复模式" in dic['con']:
                self.autoReplyMode = False
                self.webwxsendmsg("[微信机器人]:再见[皱眉]", replycommand_dst_id)
                self.robotready = dict()
            else:
                pass
        elif "机器人" in dic['con']:
            if "安静" in dic['con']:
                self.limit_autoReply = True
                self.webwxsendmsg("[微信机器人]:好的主人~我尽量保持安静！[闭嘴]", replycommand_dst_id)
                self.robot_wait_time = 30
                wTdic = {"一":60,"二":30,"三":0}
                r = dic["con"].find("级安静")
                lev = dic['con'][r-1:r]
                if lev in wTdic:
                    self.robot_wait_time = wTdic[lev]
                self.robotready = dict()
            elif "自由" in dic['con']:
                self.limit_autoReply = False
                self.webwxsendmsg("[微信机器人]:Yeah那我随便说话啦[耶]", replycommand_dst_id)
            else:
                pass
        elif "撤回终结者模式" in dic['con']:
            if "开启撤回终结者模式" in dic['con']:
                self.autoReplyRevokeMode = True
                self.webwxsendmsg("System:好的！那么[奸笑]", replycommand_dst_id)
                self.send_EMOTION_id(replycommand_dst_id, "system_on.png")
            elif "关闭撤回终结者模式" in dic['con']:
                self.autoReplyRevokeMode = False
                self.webwxsendmsg("System:既然主人发话了~", replycommand_dst_id)
                self.send_EMOTION_id(replycommand_dst_id, "system_off.png")
            else:
                pass
        elif "状态" in dic['con']:
            ans = "System:当前状态：\n"
            ans += "自动回复模式开\n" if self.autoReplyMode else "自动回复模式关\n"
            ans += "撤回终结者模式开\n" if self.autoReplyRevokeMode else "撤回终结者模式关\n"
            ans += "限制机器人说话\n" if self.limit_autoReply else "机器人可自由说话\n"
            self.webwxsendmsg(ans, replycommand_dst_id)

        elif "关闭指令" in dic['con']:
            self.webwxsendmsg("指令模式已关闭", replycommand_dst_id)
            del self.commandmode[replycommand_dst_id]

        else:
            isCommand = False

        if isCommand:
            self.commandmode[replycommand_dst_id] = time.time()
            return 0

    if self.autoReplyMode:
        if dic['con'][:3] == "机器人" or dic['con'][:6] in ["System", "system"]:
            if dic["srcName"] not in self.black_contact_dst \
                    and (dic["groupName"] in self.avalible_group_dst or dic["groupName"] == None) \
                    and msg['FromUserName'] != msg['ToUserName']:
                self.robotready[replycommand_dst_id] = time.time()
                self.webwxsendmsg("在", replycommand_dst_id)

        if replycommand_dst_id in self.robotready or not self.limit_autoReply or not dic['isGroup']:

            print("from", msg['FromUserName'], "to", msg['ToUserName'])

            ans = self._tuling( dic['con'], loc, msg['FromUserName']) + '\n[微信机器人自动回复]'  # 获得回复信息
            # ans = self._xiaodoubi( dic['con']).decode() + '\n[微信机器人自动回复]'
            if self.webwxsendmsg(ans, replycommand_dst_id):  # 发送自动回复信息
                self.robotready[replycommand_dst_id] = time.time()
                print('自动回复: ' + ans)
                logging.info('自动回复: ' + ans)
            else:
                print('自动回复失败')
                logging.info('自动回复失败')

            if replycommand_dst_id in self.robotready and dic['con'] in ["你闭嘴", "停止说话", "不要说话", "安静", "闭嘴"]:
                del self.robotready[replycommand_dst_id]

class WebWeixin(object):
    def __str__(self):
        description = \
            "=========================\n" + \
            "[#] Web Weixin\n" + \
            "[#] Debug Mode: " + str(self.DEBUG) + "\n" + \
            "[#] Uuid: " + self.uuid + "\n" + \
            "[#] Uin: " + str(self.uin) + "\n" + \
            "[#] Sid: " + self.sid + "\n" + \
            "[#] Skey: " + self.skey + "\n" + \
            "[#] DeviceId: " + self.deviceId + "\n" + \
            "[#] PassTicket: " + self.pass_ticket + "\n" + \
            "========================="
        return description

    def __init__(self,open_qr_in_cmd = True,autoReplyMode = False,autoReplyRevokeMode=False,limit_autoReply = True,interactive = False,autoOpen = False):

        self.DEBUG = False
        self.work_path = os.getcwd()
        self.work_files = {"管理员名单":"管理员名单.txt",
                      "群白名单":"群白名单.txt",
                      "黑名单":"黑名单.txt"}
        self.work_dirs=dict()
        self.init_files()
        self.Administraters = set()
        self.avalible_group_dst = set()
        self.black_contact_dst = set()
        self.commandmode = dict()
        self.command_duration = 120
        self.uuid = ''
        self.base_uri = ''
        self.redirect_uri = ''
        self.selector=''
        self.uin = ''
        self.sid = ''
        self.skey = ''
        self.pass_ticket = ''
        self.deviceId = 'e' + repr(random.random())[2:17]
        self.BaseRequest = {}
        self.synckey = ''
        self.SyncKey = []
        self.User = dict()
        self.MemberList = []
        self.ContactList = []  # 好友
        self.GroupList = []  # 群
        self.GroupMemeberList = []  # 群友
        self.PublicUsersList = []  # 公众号／服务号
        self.SpecialUsersList = []  # 特殊账号
        self.open_qr_in_cmd = open_qr_in_cmd
        self.autoReplyMode = autoReplyMode
        self.autoReplyRevokeMode = autoReplyRevokeMode
        self.limit_autoReply=limit_autoReply

        self.robotready = dict()
        self.robot_wait_time = 30 if self.limit_autoReply else 300

        self.syncHost = ''
        self.ava_SynHost_List = []
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
        self.interactive = interactive
        self.autoOpen = autoOpen
        self.saveFolder = os.path.join(os.getcwd(), 'saved')
        self.saveSubFolders = {'webwxgeticon': 'icons', 'webwxgetheadimg': 'headimgs', 'webwxgetmsgimg': 'msgimgs',
                               'webwxgetemotion': 'emotions', 'webwxgetvideo': 'videos', 'webwxgetvoice': 'voices',
                               '_showQRCodeImg': 'qrcodes'}
        self.appid = 'wx782c26e4c19acffb'
        self.lang = 'zh_CN'
        self.lastCheckTs = time.time()
        self.memberCount = 0
        self.SpecialUsers = ['newsapp', 'fmessage', 'filehelper', 'weibo', 'qqmail', 'fmessage', 'tmessage', 'qmessage',
                             'qqsync', 'floatbottle', 'lbsapp', 'shakeapp', 'medianote', 'qqfriend', 'readerapp',
                             'blogapp', 'facebookapp', 'masssendapp', 'meishiapp', 'feedsapp',
                             'voip', 'blogappweixin', 'weixin', 'brandsessionholder', 'weixinreminder',
                             'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'officialaccounts', 'notification_messages',
                             'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'wxitil', 'userexperience_alarm',
                             'notification_messages']
        self.TimeOut = 20  # 同步最短时间间隔（单位:秒）
        self.media_count = -1
        self.cookie = http.cookiejar.CookieJar()
        self.msg_Store = []
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie))
        opener.addheaders = [('User-agent', self.user_agent)]
        urllib.request.install_opener(opener)

    def init_files(cla):  # 检查工作环境和文件存在性，如果不存在报错
        for file_name in cla.work_files:
            cla.work_files[file_name] = os.path.join(cla.work_path,
                                                     cla.work_files[file_name])
            if not os.path.exists(cla.work_files[file_name]):
                open(cla.work_files[file_name],"w")
        for file_name in cla.work_dirs:
            cla.work_files[file_name] = os.path.join(cla.work_path,
                                                     cla.work_files[file_name])
            if not os.path.exists(cla.work_files[file_name]):
                os.mkdir(cla.work_files[file_name])

    def loadConfig(self, config):
        if config['DEBUG']:
            self.DEBUG = config['DEBUG']
        if config['autoReplyMode']:
            self.autoReplyMode = config['autoReplyMode']
        if config['user_agent']:
            self.user_agent = config['user_agent']
        if config['interactive']:
            self.interactive = config['interactive']
        if config['autoOpen']:
            self.autoOpen = config['autoOpen']

    def getUUID(self):
        url = 'https://login.weixin.qq.com/jslogin'
        params = {
            'appid': self.appid,
            'fun': 'new',
            'lang': self.lang,
            '_': int(time.time()),
        }
        # r = requests.get(url=url, params=params)
        # r.encoding = 'utf-8'
        # data = r.text
        data = self._post(url, params, False).decode("utf-8")
        if data == '':
            return False
        regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
        pm = re.search(regx, data)
        if pm:
            code = pm.group(1)
            self.uuid = pm.group(2)
            return code == '200'
        return False

    def genQRCode(self):
        # return self._showQRCodeImg()
        if self.open_qr_in_cmd:
            self._str2qr('https://login.weixin.qq.com/l/' + self.uuid)
        elif sys.platform.startswith('win'):
            self._showQRCodeImg('win')
        elif sys.platform.find('darwin') >= 0:
            self._showQRCodeImg('macos')
        else:
            self._str2qr('https://login.weixin.qq.com/l/' + self.uuid)

    def _showQRCodeImg(self, str):
        url = 'https://login.weixin.qq.com/qrcode/' + self.uuid
        params = {
            't': 'webwx',
            '_': int(time.time())
        }

        data = self._post(url, params, False)
        if data == '':
            return
        QRCODE_PATH = self._saveFile('qrcode.jpg', data, '_showQRCodeImg')
        if str == 'win':
            os.startfile(QRCODE_PATH)
        elif str == 'macos':
            subprocess.call(["open", QRCODE_PATH])
        else:
            return

    def waitForLogin(self, tip=1):
        time.sleep(tip)
        url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (
            tip, self.uuid, int(time.time()))
        data = self._get(url)
        if data == '':
            return False
        pm = re.search(r"window.code=(\d+);", data)
        code = pm.group(1)

        if code == '201':
            return True
        elif code == '200':
            pm = re.search(r'window.redirect_uri="(\S+?)";', data)
            r_uri = pm.group(1) + '&fun=new'
            self.redirect_uri = r_uri
            self.base_uri = r_uri[:r_uri.rfind('/')]
            return True
        elif code == '408':
            self._echo('[登陆超时] \n')
        else:
            self._echo('[登陆异常] \n')
        return False

    def login(self):
        data = self._get(self.redirect_uri)
        if data == '':
            return False
        doc = xml.dom.minidom.parseString(data)
        root = doc.documentElement

        for node in root.childNodes:
            if node.nodeName == 'skey':
                self.skey = node.childNodes[0].data
            elif node.nodeName == 'wxsid':
                self.sid = node.childNodes[0].data
            elif node.nodeName == 'wxuin':
                self.uin = node.childNodes[0].data
            elif node.nodeName == 'pass_ticket':
                self.pass_ticket = node.childNodes[0].data

        if '' in (self.skey, self.sid, self.uin, self.pass_ticket):
            return False

        self.BaseRequest = {
            'Uin': int(self.uin),
            'Sid': self.sid,
            'Skey': self.skey,
            'DeviceID': self.deviceId,
        }
        return True

    def webwxinit(self):
        url = self.base_uri + '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (
            self.pass_ticket, self.skey, int(time.time()))
        params = {
            'BaseRequest': self.BaseRequest
        }
        dic = self._post(url, params)
        if dic == '':
            return False
        self.SyncKey = dic['SyncKey']
        self.User = dic['User']

        # synckey for synccheck
        self.synckey = '|'.join(
            [str(keyVal['Key']) + '_' + str(keyVal['Val']) for keyVal in self.SyncKey['List']])

        return dic['BaseResponse']['Ret'] == 0

    def webwxstatusnotify(self):
        url = self.base_uri + \
              '/webwxstatusnotify?lang=zh_CN&pass_ticket=%s' % (self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            "Code": 3,
            "FromUserName": self.User['UserName'],
            "ToUserName": self.User['UserName'],
            "ClientMsgId": int(time.time())
        }
        dic = self._post(url, params)
        if dic == '':
            return False

        return dic['BaseResponse']['Ret'] == 0

    def webwxgetcontact(self):
        SpecialUsers = self.SpecialUsers
        url = self.base_uri + '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (
            self.pass_ticket, self.skey, int(time.time()))
        dic = self._post(url, {})
        if dic == '':
            return False

        self.MemberCount = dic['MemberCount']
        self.MemberList = dic['MemberList']
        ContactList = self.MemberList[:]
        GroupList = self.GroupList[:]
        PublicUsersList = self.PublicUsersList[:]
        SpecialUsersList = self.SpecialUsersList[:]

        for i in range(len(ContactList) - 1, -1, -1):
            Contact = ContactList[i]
            if Contact['VerifyFlag'] & 8 != 0:  # 公众号/服务号
                ContactList.remove(Contact)
                self.PublicUsersList.append(Contact)
            elif Contact['UserName'] in SpecialUsers:  # 特殊账号
                ContactList.remove(Contact)
                self.SpecialUsersList.append(Contact)
            elif '@@' in Contact['UserName']:  # 群聊
                ContactList.remove(Contact)
                self.GroupList.append(Contact)
            elif Contact['UserName'] == self.User['UserName']:  # 自己
                ContactList.remove(Contact)
        self.ContactList = ContactList

        return True

    def webwxbatchgetcontact(self):
        url = self.base_uri + \
              '/webwxbatchgetcontact?type=ex&r=%s&pass_ticket=%s' % (
                  int(time.time()), self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            "Count": len(self.GroupList),
            "List": [{"UserName": g['UserName'], "EncryChatRoomId": ""} for g in self.GroupList]
        }
        dic = self._post(url, params)
        if dic == '':
            return False

        # blabla ...
        ContactList = dic['ContactList']
        ContactCount = dic['Count']
        self.GroupList = ContactList

        for i in range(len(ContactList) - 1, -1, -1):
            Contact = ContactList[i]
            MemberList = Contact['MemberList']
            for member in MemberList:
                self.GroupMemeberList.append(member)
        return True

    def getNameById(self, id):
        url = self.base_uri + \
              '/webwxbatchgetcontact?type=ex&r=%s&pass_ticket=%s' % (
                  int(time.time()), self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            "Count": 1,
            "List": [{"UserName": id, "EncryChatRoomId": ""}]
        }
        dic = self._post(url, params)
        if dic == '':
            return None

        # blabla ...
        return dic['ContactList']

    def testsynccheck(self):
        SyncHost = [  # 'wx2.qq.com',
            'webpush.wx2.qq.com',
            'wx8.qq.com',
            'webpush.wx8.qq.com',
            'qq.com',
            'webpush.wx.qq.com',
            'web2.wechat.com',
            'webpush.web2.wechat.com',
            'wechat.com',
            'webpush.web.wechat.com',
            'webpush.weixin.qq.com',
            'webpush.wechat.com',
            'webpush1.wechat.com',
            'webpush2.wechat.com',
            'webpush.wx.qq.com',
            'webpush2.wx.qq.com']
        for host in SyncHost:
            self.syncHost = host
            [retcode, selector] = self.synccheck()
            if retcode == '0':
                print("syncHost为:", self.syncHost)
                return True
        return False

    def synccheck(self):
        params = {
            'r': int(time.time()),
            'sid': self.sid,
            'uin': self.uin,
            'skey': self.skey,
            'deviceid': self.deviceId,
            'synckey': self.synckey,
            '_': int(time.time()),
        }
        url = 'https://' + self.syncHost + '/cgi-bin/mmwebwx-bin/synccheck?' + urllib.parse.urlencode(params)
        #print(url)
        data = self._get(url)
        if data == '':
            return [-1, -1]

        pm = re.search(
            r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}', data)
        retcode = pm.group(1)
        selector = pm.group(2)
        return [retcode, selector]

    def webwxsync(self):
        url = self.base_uri + \
              '/webwxsync?sid=%s&skey=%s&pass_ticket=%s' % (
                  self.sid, self.skey, self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            'SyncKey': self.SyncKey,
            'rr': ~int(time.time())
        }
        dic = self._post(url, params)
        if dic == '':
            return None
        if self.DEBUG:
            print(json.dumps(dic, indent=4))
            (json.dumps(dic, indent=4))

        if dic['BaseResponse']['Ret'] == 0:
            self.SyncKey = dic['SyncCheckKey']
            self.synckey = '|'.join(
                [str(keyVal['Key']) + '_' + str(keyVal['Val']) for keyVal in self.SyncKey['List']])
        if dic is not None:
            if len(dic['AddMsgList']) != 0:
                try:
                    self.handleMsg(dic)
                except Exception:
                    import traceback
                    traceback.print_exc()
                    logging.error('generic exception: ' + traceback.format_exc())
            if len(dic['ModContactList']) != 0:
                self.webwxsendmsg("接收到ModContactList列表selector=%s" % self.selector, self.User['UserName'])
                #for x in dic['ModContactList']:
                #    self.webwxsendmsg(str(x), self.User['UserName'])
        return dic

    def webwxsendmsg(self, word, to='filehelper'):
        url = self.base_uri + \
              '/webwxsendmsg?pass_ticket=%s' % (self.pass_ticket)
        clientMsgId = str(int(time.time() * 1000)) + \
                      str(random.random())[:5].replace('.', '')
        params = {
            'BaseRequest': self.BaseRequest,
            'Msg': {
                "Type": 1,
                "Content": self._transcoding(word),
                "FromUserName": self.User['UserName'],
                "ToUserName": to,
                "LocalID": clientMsgId,
                "ClientMsgId": clientMsgId
            }
        }
        headers = {'content-type': 'application/json; charset=UTF-8'}
        data = json.dumps(params, ensure_ascii=False).encode('utf8')
        r = requests.post(url, data=data, headers=headers)
        dic = r.json()

        self.webwxsync()

        return dic['BaseResponse']['Ret'] == 0

    def Do_webwxsync(self):
        r = self.webwxsync()
        if r is not None:
            if len(r['AddMsgList']) != 0:
                try:
                    self.handleMsg(r)
                except Exception:
                    import traceback
                    traceback.print_exc()
                    logging.error('generic exception: ' + traceback.format_exc())
            if len(r['ModContactList']) != 0:
                self.webwxsendmsg("接收到ModContactList列表selector=%s" % self.selector, self.User['UserName'])
                for x in r['ModContactList']:
                    self.webwxsendmsg(str(x), self.User['UserName'])


    def webwxuploadmedia(self, image_name):
        url = 'https://file2.wx.qq.com/cgi-bin/mmwebwx-bin/webwxuploadmedia?f=json'
        # 计数器
        self.media_count = self.media_count + 1
        # 文件名
        file_name = image_name
        # MIME格式
        # mime_type = application/pdf, image/jpeg, image/png, etc.
        mime_type = mimetypes.guess_type(image_name, strict=False)[0]
        # 微信识别的文档格式，微信服务器应该只支持两种类型的格式。pic和doc
        # pic格式，直接显示。doc格式则显示为文件。
        media_type = 'pic' if mime_type.split('/')[0] == 'image' else 'doc'
        # 上一次修改日期
        lastModifieDate = 'Thu Mar 17 2016 00:55:10 GMT+0800 (CST)'
        # 文件大小
        file_size = os.path.getsize(file_name)
        # PassTicket
        pass_ticket = self.pass_ticket
        # clientMediaId
        client_media_id = str(int(time.time() * 1000)) + \
                          str(random.random())[:5].replace('.', '')
        # webwx_data_ticket
        webwx_data_ticket = ''
        for item in self.cookie:
            if item.name == 'webwx_data_ticket':
                webwx_data_ticket = item.value
                break
        if (webwx_data_ticket == ''):
            return "None Fuck Cookie"

        uploadmediarequest = json.dumps({
            "BaseRequest": self.BaseRequest,
            "ClientMediaId": client_media_id,
            "TotalLen": file_size,
            "StartPos": 0,
            "DataLen": file_size,
            "MediaType": 4
        }, ensure_ascii=False).encode('utf8')

        multipart_encoder = MultipartEncoder(
            fields={
                'id': 'WU_FILE_' + str(self.media_count),
                'name': file_name,
                'type': mime_type,
                'lastModifieDate': lastModifieDate,
                'size': str(file_size),
                'mediatype': media_type,
                'uploadmediarequest': uploadmediarequest,
                'webwx_data_ticket': webwx_data_ticket,
                'pass_ticket': pass_ticket,
                'filename': (file_name, open(file_name, 'rb'), mime_type.split('/')[1])
            },
            boundary='-----------------------------1575017231431605357584454111'
        )

        headers = {
            'Host': 'file2.wx.qq.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:42.0) Gecko/20100101 Firefox/42.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://wx2.qq.com/',
            'Content-Type': multipart_encoder.content_type,
            'Origin': 'https://wx2.qq.com',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }

        r = requests.post(url, data=multipart_encoder, headers=headers)
        response_json = r.json()
        if response_json['BaseResponse']['Ret'] == 0:
            return response_json
        return None

    def webwxsendmsgimg(self, user_id, media_id):
        url = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsgimg?fun=async&f=json&pass_ticket=%s' % self.pass_ticket
        clientMsgId = str(int(time.time() * 1000)) + \
                      str(random.random())[:5].replace('.', '')
        data_json = {
            "BaseRequest": self.BaseRequest,
            "Msg": {
                "Type": 3,
                "MediaId": media_id,
                "FromUserName": self.User['UserName'],
                "ToUserName": user_id,
                "LocalID": clientMsgId,
                "ClientMsgId": clientMsgId
            }
        }
        headers = {'content-type': 'application/json; charset=UTF-8'}
        data = json.dumps(data_json, ensure_ascii=False).encode('utf8')
        r = requests.post(url, data=data, headers=headers)
        dic = r.json()
        self.webwxsync()
        return dic['BaseResponse']['Ret'] == 0

    def webwxsendmsgemotion(self, user_id, media_id):
        url = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendemoticon?fun=sys&f=json&pass_ticket=%s' % self.pass_ticket
        clientMsgId = str(int(time.time() * 1000)) + \
                      str(random.random())[:5].replace('.', '')
        data_json = {
            "BaseRequest": self.BaseRequest,
            "Msg": {
                "Type": 47,
                "EmojiFlag": 2,
                "MediaId": media_id,
                "FromUserName": self.User['UserName'],
                "ToUserName": user_id,
                "LocalID": clientMsgId,
                "ClientMsgId": clientMsgId
            }
        }
        headers = {'content-type': 'application/json; charset=UTF-8'}
        data = json.dumps(data_json, ensure_ascii=False).encode('utf8')
        r = requests.post(url, data=data, headers=headers)
        dic = r.json()
        if self.DEBUG:
            print(json.dumps(dic, indent=4))
            logging.debug(json.dumps(dic, indent=4))
        return dic['BaseResponse']['Ret'] == 0

    def _saveFile(self, filename, data, api=None):
        fn = filename
        if self.saveSubFolders[api]:
            dirName = os.path.join(self.saveFolder, self.saveSubFolders[api])
            if not os.path.exists(dirName):
                os.makedirs(dirName)
            fn = os.path.join(dirName, filename)
            logging.debug('Saved file: %s' % fn)
            with open(fn, 'wb') as f:
                f.write(data)
                f.close()
        return fn

    def webwxgeticon(self, id):
        url = self.base_uri + \
              '/webwxgeticon?username=%s&skey=%s' % (id, self.skey)
        data = self._get(url)
        if data == '':
            return ''
        fn = 'img_' + id + '.jpg'
        return self._saveFile(fn, data, 'webwxgeticon')

    def webwxgetheadimg(self, id):
        url = self.base_uri + \
              '/webwxgetheadimg?username=%s&skey=%s' % (id, self.skey)
        data = self._get(url)
        if data == '':
            return ''
        fn = 'img_' + id + '.jpg'
        return self._saveFile(fn, data, 'webwxgetheadimg')

    def get_EMOTION_from_msg(self, content, msgid):
        url = self._searchContent('cdnurl', content)
        data = urllib.request.urlopen(url).read()
        fn = "emo_" + msgid + ".gif"
        # return self._saveFile(fn, data, 'webwxgetemotion')
        return self.get_pic_from_url(url, fn)

    def webwxgetmsgimg(self, msgid):
        url = self.base_uri + \
              '/webwxgetmsgimg?MsgID=%s&skey=%s' % (msgid, self.skey)
        data = urllib.request.urlopen(url).read()
        fn = 'img_' + msgid + '.jpg'
        return self.get_pic_from_url(url, fn)

        # return self._saveFile(fn, data, 'webwxgetmsgimg')

    # Not work now for weixin haven't support this API
    def webwxgetvideo(self, msgid):
        url = self.base_uri + \
              '/webwxgetvideo?msgid=%s&skey=%s' % (msgid, self.skey)
        data = self._get(url, api='webwxgetvideo')
        if data == '':
            return ''
        fn = 'video_' + msgid + '.mp4'
        return self._saveFile(fn, data, 'webwxgetvideo')

    def webwxgetvoice(self, msgid):
        url = self.base_uri + \
              '/webwxgetvoice?msgid=%s&skey=%s' % (msgid, self.skey)
        data = self._get(url)
        if data == '':
            return ''
        fn = 'voice_' + msgid + '.mp3'
        return self._saveFile(fn, data, 'webwxgetvoice')

    def getGroupName(self, id):
        name = '未知群'
        for member in self.GroupList:
            if member['UserName'] == id:
                name = member['NickName']
        if name == '未知群':
            # 现有群里面查不到
            GroupList = self.getNameById(id)
            for group in GroupList:
                self.GroupList.append(group)
                if group['UserName'] == id:
                    name = group['NickName']
                    MemberList = group['MemberList']
                    for member in MemberList:
                        self.GroupMemeberList.append(member)
        return name

    def getUserRemarkorNickName(self, id, NickNameava = True):
        name = '未知群' if id[:2] == '@@' else '陌生人'
        if id == self.User['UserName']:
            name = self.User['NickName']  # 自己

        if id[:2] == '@@':
            # 群
            name = self.getGroupName(id)
        else:
            # 特殊账号
            for member in self.SpecialUsersList:
                if member['UserName'] == id:
                    name = member['RemarkName'] if member[
                        'RemarkName'] else member['NickName']

            # 公众号或服务号
            for member in self.PublicUsersList:
                if member['UserName'] == id:
                    name = member['RemarkName'] if member[
                        'RemarkName'] else member['NickName']

            # 直接联系人
            for member in self.ContactList:
                if member['UserName'] == id:
                    if member['RemarkName']:
                        name = member['RemarkName']
                    elif NickNameava:
                        name = member['NickName']


            # 群友
            for member in self.GroupMemeberList:
                if member['UserName'] == id:
                    if member['DisplayName']:
                        name = member['DisplayName']
                    elif NickNameava:
                        name = member['NickName']

        if name == '未知群' or name == '陌生人':
            logging.debug(id)
        return _formate_Name(name)

    def getUSerID(self, name):
        for member in self.MemberList:
            if name in [ member['RemarkName'], member['NickName'], member['UserName']] :
                return member['UserName']
        return None

    def _showMsg(self, message):

        con = None
        srcName = None
        src_id = None
        dstName = None
        dst_id = None
        groupName = None
        group_id = None
        content = None
        message_id = None
        msg = message
        logging.debug(msg)
        createtime = None
        srcRemarkName = None
        isSelf = False
        isGroup = False

        if msg['raw_msg']:
            srcRemarkName = self.getUserRemarkorNickName(msg['raw_msg']['FromUserName'],NickNameava=False)
            srcName = self.getUserRemarkorNickName(msg['raw_msg']['FromUserName'])  # 消息发送者名字
            src_id = msg['raw_msg']['FromUserName']
            dstName = self.getUserRemarkorNickName(msg['raw_msg']['ToUserName'])
            dst_id = msg['raw_msg']['ToUserName']  # 消息目的地
            con = _format_text(msg['raw_msg']['Content'].replace(
                '&lt;', '<').replace('&gt;', '>'))
            content = con
            message_id = msg['raw_msg']['MsgId']  # 消息id


            createtime = msg['raw_msg']['CreateTime']  # 消息创建时间

            if content.find('http://weixin.qq.com/cgi-bin/redirectforward?args=') != -1:
                # 地理位置消息
                data = self._get(content)
                if data == '':
                    return
                data.decode('gbk').encode('utf-8')
                pos = self._searchContent('title', data, 'xml')
                temp = self._get(content)
                if temp == '':
                    return
                tree = html.fromstring(temp)
                url = tree.xpath('//html/body/div/img')[0].attrib['src']
                loc = ''
                for item in urlparse(url).query.split('&'):
                    if item.split('=')[0] == 'center':
                        loc = item.split('=')[-1:]

                content = '%s 发送了一个 位置消息 - 我在 [%s](%s) @ %s]' % (
                    srcName, pos, url, loc)
            if msg['raw_msg']['ToUserName'] == 'filehelper':
                # 文件传输助手
                dstName = '文件传输助手'

            if msg['raw_msg']['FromUserName'][:2] == '@@':
                print("消息来自群:", self.getGroupName(dst_id))
                isGroup = True

                # 接收到来自群的消息
                groupName = srcName
                group_id = msg['raw_msg']['FromUserName']
                dst_id =group_id
                if ":<br/>" in con:
                    [src_id, con] = con.split(':<br/>', 1)  # people 发信人user_id,content
                    srcRemarkName = self.getUserRemarkorNickName(src_id,NickNameava=False)
                    srcName = self.getUserRemarkorNickName(src_id)
                    dstName = 'GROUP'
                else:
                    srcRemarkName = None
                    srcName = 'SYSTEM'




            if msg['raw_msg']['FromUserName'] == self.User['UserName']:
                srcName = self.User['NickName']
                src_id = self.User['UserName']
                # if groupName in self.avalible_group_dst:
                isSelf = True

                if msg['raw_msg']['ToUserName'][:2] == '@@':
                    # 自己发给群的消息
                    isGroup = True
                    print("自己发去的群为:", dstName)
                    groupName = dstName
                    group_id = dst_id
                    dstName = 'GROUP'

            # 收到了红包

            if content == '收到红包，请在手机上查看':
                msg['message'] = content

            # 指定了消息内容
            if 'message' in list(msg.keys()):
                content = msg['message']

        if groupName != None:
            print('%s |%s| %s -> %s: %s' % (
                message_id, groupName.strip(), srcName.strip(), dstName.strip(), content.replace('<br/>', '\n')))
            logging.info('%s |%s| %s -> %s: %s' % (message_id, groupName.strip(),
                                                   srcName.strip(), dstName.strip(), content.replace('<br/>', '\n')))
        else:
            print('%s %s -> %s: %s' % (message_id, srcName.strip(), dstName.strip(), content.replace('<br/>', '\n')))
            logging.info('%s %s -> %s: %s' % (message_id, srcName.strip(),
                                              dstName.strip(), content.replace('<br/>', '\n')))
        return {
                'srcName': srcName,
            'src_id':src_id,
                'dstName':dstName,
            'dst_id': dst_id,
            'groupName': groupName,
            'group_id':group_id,
            'msgType': msg['raw_msg']['MsgType'],
                'con': con,
                'message_id': message_id,
                'createtime': createtime,
                'srcRemarkName':srcRemarkName,
        'isSelf':isSelf,
        'isGroup':isGroup}

    def get_msg_From_userid(self, msg):
        if msg['FromUserName'][:2] == '@@':
            return msg['Content'][:msg['Content'].find(':<br/>')]
        else:
            return msg['FromUserName']

    def get_pic_from_url(self, url, file):
        picture = urllib.request.urlopen(url).read()
        local = open(file, 'wb')
        local.write(picture)
        local.close()
        return file

    def save_list(self,file,list):
        f = open(file, "w", encoding="utf-8")
        f.write("\n".join(list))
        f.close()

    def read_list(self,file):

        f = open(file, "rb")
        data=f.read()

        if data[:3] == codecs.BOM_UTF8:
            data = data[3:].decode("utf-8")
        else:
            data = data.decode("utf-8")
        if len(data) == 0:
            return []
        list=data.split("\r\n")
        f.close()
        return list
    def handleMsg(self, r):
        for msg in r['AddMsgList']:
            print('[*] 你有新的消息，请注意查收')
            logging.debug('[*] 你有新的消息，请注意查收')

            if self.DEBUG:
                fn = 'msg' + str(int(random.random() * 1000)) + '.json'
                with open(fn, 'w') as f:
                    f.write(json.dumps(msg))
                print('[*] 该消息已储存到文件: ' + fn)
                logging.debug('[*] 该消息已储存到文件: %s' % (fn))
            msgType = msg['MsgType']
            loc = msg['RecommendInfo']['Province'] + msg['RecommendInfo']['City']
            name = self.getUserRemarkorNickName(msg['FromUserName'])
            msgid = msg['MsgId']
            createtime = msg['CreateTime']

            if msgType == 1:
                raw_msg = {'raw_msg': msg}
                dic = self._showMsg(raw_msg)
                replycommand_dst_id = dic['dst_id']

                _reaction_Msg1(self, dic, msg, loc)

            elif msgType == 3:
                image = self.webwxgetmsgimg(msgid)
                raw_msg = {'raw_msg': msg,
                           'message': '%s 发送了一张图片: %s' % (name, image)}
                dic = self._showMsg(raw_msg)
                dic['con'] = image
                self._safe_open(image)
            elif msgType == 34:
                voice = self.webwxgetvoice(msgid)
                raw_msg = {'raw_msg': msg,
                           'message': '%s 发了一段语音: %s' % (name, voice)}
                dic = self._showMsg(raw_msg)
                dic['con'] = voice

                self._safe_open(voice)
            elif msgType == 42:
                info = msg['RecommendInfo']
                con = ('%s 发送了一张名片:\n' % name
                       + '=========================\n'
                       + '= 昵称: %s\n' % info['NickName']
                       + '= 微信号: %s\n' % info['Alias']
                       + '= 地区: %s %s' % (info['Province'], info['City'])
                       + '= 性别: %s\n' % ['未知', '男', '女'][info['Sex']]
                       + '=========================\n')
                print(con)
                # print('%s 发送了一张名片:' % name)
                # print('=========================')
                # print('= 昵称: %s' % info['NickName'])
                # print('= 微信号: %s' % info['Alias'])
                # print('= 地区: %s %s' % (info['Province'], info['City']))
                # print('= 性别: %s' % ['未知', '男', '女'][info['Sex']])
                # print('=========================')
                raw_msg = {'raw_msg': msg, 'message': '%s 发送了一张名片: %s' % (
                    name.strip(), json.dumps(info))}
                dic = self._showMsg(raw_msg)
                dic['con'] = con

            elif msgType == 47:

                emo = self.webwxgetmsgimg(msgid)
                raw_msg = {'raw_msg': msg,
                           'message': '%s 发了一个动画表情，点击下面链接查看: %s' % (name, emo)}
                dic = self._showMsg(raw_msg)
                dic['con'] = emo

                self._safe_open(emo)
            elif msgType == 49:
                appMsgType = defaultdict(lambda: "")
                appMsgType.update({5: '链接', 3: '音乐', 7: '微博'})

                con = ('%s 分享了一个%s:' % (name, appMsgType[msg['AppMsgType']])
                       + '========================='
                       + '= 标题: %s' % msg['FileName']
                       + '= 描述: %s' % self._searchContent('des', dic['con'], 'xml')
                       + '= 链接: %s' % msg['Url']
                       + '= 来自: %s' % self._searchContent('appname', dic['con'], 'xml')
                       + '=========================')
                print(con)

                # print('%s 分享了一个%s:' % (name, appMsgType[msg['AppMsgType']]))
                # print('=========================')
                # print('= 标题: %s' % msg['FileName'])
                # print('= 描述: %s' % self._searchContent('des', dic['con'], 'xml'))
                # print('= 链接: %s' % msg['Url'])
                # print('= 来自: %s' % self._searchContent('appname', dic['con'], 'xml'))
                # print('=========================')
                card = {
                    'title': msg['FileName'],
                    'description': self._searchContent('des', dic['con'], 'xml'),
                    'url': msg['Url'],
                    'appname': self._searchContent('appname', dic['con'], 'xml')
                }
                raw_msg = {'raw_msg': msg, 'message': '%s 分享了一个%s: %s' % (
                    name, appMsgType[msg['AppMsgType']], json.dumps(card))}
                dic = self._showMsg(raw_msg)
                dic['con'] = con

            elif msgType == 51:
                raw_msg = {'raw_msg': msg, 'message': '[*] 检测到你在活动'}
                dic = self._showMsg(raw_msg)
            elif msgType in (62,43):
                video = self.webwxgetvideo(msgid)
                raw_msg = {'raw_msg': msg,
                           'message': '%s 发了一段小视频: %s' % (name, video)}
                dic = self._showMsg(raw_msg)
                dic['con'] = video

                self._safe_open(video)
            elif msgType == 10002:
                raw_msg = {'raw_msg': msg, 'message': '%s 撤回了一条消息' % name}
                dic = self._showMsg(raw_msg)
                if self.autoReplyRevokeMode:
                    oldmsgid = dic['con'][dic['con'].find('<msgid>') + 7:dic['con'].find('</msgid>')]
                    self.resend_revoked_msg(oldmsgid)
            elif msgType == 10000:
                raw_msg = {'raw_msg': msg, 'message': '%s 系统消息' % name}
                dic = self._showMsg(raw_msg)
                if '修改群名为' in dic['con'] and dic['groupName'] in self.avalible_group_dst:
                    #new_groupname=content[content.find('“')+1:content.find('”')]
                    length=len(self.GroupList);i=0
                    while i < length:
                        if self.GroupList[i]['UserName'] == dic['dst_id']:
                            del self.GroupList[i]
                            i-=1
                            length-=1
                        i+=1
                    new_groupname=self.getGroupName(dic['dst_id'])
                    self.avalible_group_dst.remove(dic['groupName'])
                    self.avalible_group_dst.add(new_groupname)
                    self.webwxsendmsg("已成功把群%s移除白名单并把群%s加入白名单"%(dic['groupName'],new_groupname), dic['dst_id'])
                    self.save_list("群白名单.txt", self.avalible_group_dst)

                self.webwxsendmsg(dic['con'], 'filehelper')
            else:
                logging.debug('[*] 该消息类型为: %d，可能是表情，图片, 链接或红包: %s' %
                              (msg['MsgType'], json.dumps(msg)))
                raw_msg = {
                    'raw_msg': msg, 'message': '[*] 该消息类型为: %d，可能是表情，图片, 链接或红包' % msg['MsgType']}
                dic = self._showMsg(raw_msg)
                dic['con'] = '[*] 未识别的消息类型: %d，可能是表情，图片, 链接或红包,内容为 %s' %( msg['MsgType'],dic['con'])
            # 自己加的代码-------------------------------------------#

            self.msg_Store.append(dic)
            i = 0
            while i < len(self.msg_Store):
                if time.time() - self.msg_Store[i]["createtime"] >= 600:
                    if self.msg_Store[i]["msgType"] in [3, 34, 47, 62]:
                        os.remove(self.msg_Store[i]['con'])
                    del self.msg_Store[i];
                    i -= 1
                i += 1
        return 1
                    # 自己加的代码-------------------------------------------#

    def resend_revoked_msg(self, oldmsgid):



        for m in self.msg_Store:  # {'dst_id': dst_id,'srcName': srcName,'con': con,'message_id': message_id,'createtime': createtime}
            if m['isSelf']:
                revoke_dstid = m['dst_id']
            else:
                revoke_dstid = m['src_id']

            if m["isGroup"]:
                if m["groupName"] in self.avalible_group_dst:
                    revoke_dstid = m["group_id"]
                else:
                    revoke_dstid = 'filehelper'


            if m["message_id"] == oldmsgid:
                if m["msgType"] == 1 or m["msgType"] == 42 or m["msgType"] == 49:
                    ans = "System：刚才" + m["srcName"] + "撤回了:\n\"" + m["con"] + "\"\n但是我看到了哈哈哈哈"
                    self.webwxsendmsg(ans, revoke_dstid)
                    self.send_EMOTION_id(revoke_dstid, "system.png")
                elif m["msgType"] == 3:
                    self.webwxsendmsg("System：刚才" + m["srcName"] + "撤回了:", revoke_dstid)
                    self.send_IMG_id(revoke_dstid, m['con'])
                    self.webwxsendmsg("但是我看到了哈哈哈哈", revoke_dstid)
                    self.send_EMOTION_id(revoke_dstid, "system.png")
                elif m["msgType"] == 34:
                    self.webwxsendmsg("System：刚才" + m["srcName"] + "撤回了一段语音:", revoke_dstid)
                    # 文件
                    self.webwxsendmsg("但是我听完了哈哈哈哈", revoke_dstid)
                    self.send_EMOTION_id(revoke_dstid, "system.png")
                elif m["msgType"] == 47:
                    self.webwxsendmsg("System：刚才" + m["srcName"] + "撤回了:", revoke_dstid)
                    self.send_EMOTION_id(revoke_dstid, m['con'])  # 发送动态表情才对
                    self.webwxsendmsg("但是我看到了哈哈哈哈", revoke_dstid)
                    self.send_EMOTION_id(revoke_dstid, "system.png")
                elif m["msgType"] in (62,43):
                    self.webwxsendmsg("System：刚才" + m["srcName"] + "撤回了一段视频:", revoke_dstid)
                    # 文件
                    self.webwxsendmsg("但是我看完了哈哈哈哈", revoke_dstid)
                    self.send_EMOTION_id(revoke_dstid, "system.png")
                else:
                    ans = "System：刚才" + m["srcName"] + "撤回了:\n\"" + m["con"] + "\"\n虽然我还识别不了但是我保存了哈哈哈哈"
                    self.webwxsendmsg(ans, revoke_dstid)
                    self.send_EMOTION_id(revoke_dstid, "system.png")
                break

    def send_IMG_id(self, user_id, file_path):
        response = self.webwxuploadmedia(file_path)
        if response is not None:
            media_id = response['MediaId']
            self.webwxsendmsgimg(user_id, media_id)
        else:
            print("response is None")

    def send_EMOTION_id(self, user_id, file_path):
        response = self.webwxuploadmedia(file_path)
        if response is not None:
            media_id = response['MediaId']
            self.webwxsendmsgemotion(user_id, media_id)
        else:
            print("response is None")

    def listenFuncs(self):
        # robotready

        delname = []
        for replycommand_dst_id in self.robotready:
            if time.time() - self.robotready[replycommand_dst_id] > self.robot_wait_time:
                delname.append(replycommand_dst_id)

        for name in delname:

            del self.robotready[name]

        delname = []
        for replycommand_dst_id in self.commandmode:
            if time.time() - self.commandmode[replycommand_dst_id] > self.command_duration:
                delname.append(replycommand_dst_id)
        for name in delname:
            self.webwxsendmsg("指令模式已关闭", name)
            del self.commandmode[name]

    def listenMsgMode(self):
        print('[*] 进入消息监听模式 ... 成功')
        logging.debug('[*] 进入消息监听模式 ... 成功')
        playWeChat = 0
        redEnvelope = 0
        error_n = 0
        try_n = 0
        line = 0
        self.syncHost = self.ava_SynHost_List[line]
        while True:
            self.listenFuncs()
            may_e=0
            self.lastCheckTs = time.time()
            [retcode, self.selector] = self.synccheck()
            print('retcode: %s, selector: %s' % (retcode, self.selector))
            if self.DEBUG:
                print('retcode: %s, selector: %s' % (retcode, self.selector))
            logging.debug('retcode: %s, selector: %s' % (retcode, self.selector))

            if retcode == '1100':
                print('[*] 你在手机上登出了微信，债见')
                logging.debug('[*] 你在手机上登出了微信，债见')
                break
            if retcode == '1101':
                print('[*] 你在其他地方登录了 WEB 版微信，债见')
                logging.debug('[*] 你在其他地方登录了 WEB 版微信，债见')
                break
            elif retcode == '0':
                if self.selector == '2':
                    self.webwxsync()

                # elif self.selector == '6':
                #     # TODO
                #     redEnvelope += 1
                #     print('[*] 收到疑似红包消息 %d 次' % redEnvelope)
                #     logging.debug('[*] 收到疑似红包消息 %d 次' % redEnvelope)
                #     if redEnvelope >= 20:
                #         line = (line + 1) % len(self.ava_SynHost_List)
                #         print(line)
                #         self.syncHost = self.ava_SynHost_List[line]
                # elif self.selector == '7':
                #     playWeChat += 1
                #     print('[*] 你在手机上玩微信被我发现了 %d 次' % playWeChat)
                #     logging.debug('[*] 你在手机上玩微信被我发现了 %d 次' % playWeChat)
                #     r = self.webwxsync()
                elif self.selector == '0':
                    pass
                else:
                    self.webwxsync()
                    may_e=1

            if (time.time() - self.lastCheckTs) <= 10 and may_e:
                time.sleep(1)
                error_n+=1
                if error_n >= 3:
                    self.webwxsendmsg(self.selector, self.User['UserName'])
                    error_n=0
                    try_n +=1
                if try_n >3:
                    self._run('[*] 尝试重新开启状态通知 ... ', self.webwxstatusnotify)
                    self.webwxsendmsg('[*] 尝试重新开启状态通知 ... 成功 selector='+self.selector, self.User['UserName'])
                    try_n=0
            time.sleep(random.randint(0,5))

    def sendMsg(self, name, word, isfile=False):
        id = self.getUSerID(name)
        if id:
            if isfile:
                with open(word, 'r') as f:
                    for line in f.readlines():
                        line = line.replace('\n', '')
                        self._echo('-> ' + name + ': ' + line)
                        if self.webwxsendmsg(line, id):
                            print(' [成功]')
                        else:
                            print(' [失败]')
                        time.sleep(1)
            else:
                if self.webwxsendmsg(word, id):
                    print('[*] 消息发送成功')
                    logging.debug('[*] 消息发送成功')
                else:
                    print('[*] 消息发送失败')
                    logging.debug('[*] 消息发送失败')
        else:
            print('[*] 此用户不存在')
            logging.debug('[*] 此用户不存在')

    def sendMsgToAll(self, word):
        for contact in self.ContactList:
            name = contact['RemarkName'] if contact[
                'RemarkName'] else contact['NickName']
            id = contact['UserName']
            self._echo('-> ' + name + ': ' + word)
            if self.webwxsendmsg(word, id):
                print(' [成功]')
            else:
                print(' [失败]')
            time.sleep(1)

    def sendImg(self, name, file_name):
        response = self.webwxuploadmedia(file_name)
        media_id = ""
        if response is not None:
            media_id = response['MediaId']
        user_id = self.getUSerID(name)
        response = self.webwxsendmsgimg(user_id, media_id)

    def sendEmotion(self, name, file_name):
        response = self.webwxuploadmedia(file_name)
        media_id = ""
        if response is not None:
            media_id = response['MediaId']
        user_id = self.getUSerID(name)
        response = self.webwxsendmsgemotion(user_id, media_id)

    @catchKeyboardInterrupt
    def start(self):
        self._echo('[*] 微信网页版 ... 开动')
        print()
        logging.debug('[*] 微信网页版 ... 开动')
        while True:
            self._run('[*] 正在获取 uuid ... ', self.getUUID)
            self._echo('[*] 正在获取二维码 ... 成功')
            print()
            logging.debug('[*] 微信网页版 ... 开动')
            # self.print_qr_cmd()
            self.genQRCode()
            print('[*] 请使用微信扫描二维码以登录 ... ')
            if not self.waitForLogin():
                continue
                print('[*] 请在手机上点击确认以登录 ... ')
            if not self.waitForLogin(0):
                continue
            break

        self._run('[*] 正在登录 ... ', self.login)
        self._run('[*] 微信初始化 ... ', self.webwxinit)
        self._run('[*] 开启状态通知 ... ', self.webwxstatusnotify)
        self._run('[*] 获取联系人 ... ', self.webwxgetcontact)
        self._echo('[*] 应有 %s 个联系人，读取到联系人 %d 个' %
                   (self.MemberCount, len(self.MemberList)))
        print()
        self._echo('[*] 共有 %d 个群 | %d 个直接联系人 | %d 个特殊账号 ｜ %d 公众号或服务号' % (len(self.GroupList),
                                                                         len(self.ContactList),
                                                                         len(self.SpecialUsersList),
                                                                         len(self.PublicUsersList)))
        print()
        self._run('[*] 获取群 ... ', self.webwxbatchgetcontact)
        logging.debug('[*] 微信网页版 ... 开动')

        if self.DEBUG:
            print(self)
        logging.debug(self)

        if self.interactive:
            if input('[*] 是否开启自动回复模式(y/n): ') == 'y':
                self.autoReplyMode = True
                print('[*] 自动回复模式 ... 开启')
                logging.debug('[*] 自动回复模式 ... 开启')
            else:
                self.autoReplyMode = False
                print('[*] 自动回复模式 ... 关闭')
                logging.debug('[*] 自动回复模式 ... 关闭')
            if input('[*] 是否开启自动恢复撤回模式(y/n): ') == 'y':
                self.autoReplyRevokeMode = True
                print('[*] 自动恢复撤回模式 ... 开启')
                logging.debug('[*] 自动恢复撤回模式 ... 开启')
            else:
                self.autoReplyRevokeMode = False
                print('[*] 自动恢复撤回模式 ... 关闭')
                logging.debug('[*] 自动恢复撤回模式 ... 关闭')
        else:
            if self.autoReplyMode:
                print('[*] 自动回复模式 ... 默认开启')
                logging.debug('[*] 自动回复模式 ... 默认开启')
            if self.autoReplyRevokeMode:
                print('[*] 自动恢复撤回模式 ... 已开启')
                logging.debug('[*] 自动恢复撤回模式 ... 已开启')

        self.Administraters = set(self.read_list(self.work_files["管理员名单"]))
        self.avalible_group_dst = set(self.read_list(self.work_files["群白名单"]))
        self.black_contact_dst = set(self.read_list(self.work_files["黑名单"]))
        print("[*] 白名单是", self.avalible_group_dst)
        self._run('[*] 进行同步线路测试 ... ', self.find_ava_SyncHost)
        print("[*] 可用同步host为：", '、'.join(i for i in self.ava_SynHost_List))
        # if sys.platform.startswith('win'):
        #     t = threading.Thread(target=self.order)
        #     t.start()
        # else:
        #     listenProcess = multiprocessing.Process(target=self.order)
        #     listenProcess.start()

        for con in self.ContactList:
            if con["NickName"] == "Gabriel":
                print(con)
        self.listenMsgMode()


    def order(self):
        while True:
            text = input('\n等待输入命令>')

            if text == 'quit':
                print('[*] 退出微信')
                logging.debug('[*] 退出微信')
                exit()
            elif text[:2] == '->':
                [name, word] = text[2:].split(':')
                if name == 'all':
                    self.sendMsgToAll(word)
                else:
                    self.sendMsg(name, word)
            elif text[:3] == 'm->':
                [name, file] = text[3:].split(':')
                self.sendMsg(name, file, True)
            elif text[:3] == 'f->':
                print('发送文件')
                logging.debug('发送文件')
            elif text[:3] == 'i->':
                print('发送图片')
                [name, file_name] = text[3:].split(':')
                self.sendImg(name, file_name)
                logging.debug('发送图片')
            elif text[:3] == 'e->':
                print('发送表情')
                [name, file_name] = text[3:].split(':')
                self.sendEmotion(name, file_name)
                logging.debug('发送表情')
    def _safe_open(self, path):
        if self.autoOpen:
            if platform.system() == "Linux":
                os.system("xdg-open %s &" % path)
            else:
                os.system('open %s &' % path)

    def _run(self, str, func, *args):
        self._echo(str)
        if func(*args):
            print('成功')
            logging.debug('%s... 成功' % (str))
        else:
            print('失败\n[*] 退出程序')
            logging.debug('%s... 失败' % (str))
            logging.debug('[*] 退出程序')
            exit()

    def _echo(self, str):
        sys.stdout.write(str)
        sys.stdout.flush()

    def _printQR(self, mat):

        BLACK = Back.BLACK + '  '
        WHITE = Back.WHITE + '  '
        for i in mat:
            print(''.join([BLACK if j else WHITE for j in i]))

    def _str2qr(self, str):
        print(str)
        qr = qrcode.QRCode()
        qr.border = 1
        qr.add_data(str)
        qr.make()
        # img = qr.make_image()
        # img.save("qrcode.png")
        mat = qr.get_matrix()
        self._printQR(mat)  # qr.print_tty() or qr.print_ascii()
        # qr.print_ascii(invert=True)

    def _transcoding(self, data):
        if not data:
            return data
        result = None
        if type(data) == str:
            result = data
        elif type(data) == bytes:
            result = data.decode('utf-8')
        return result

    def _get(self, url, api= None):
        request = urllib.request.Request(url=url)
        request.add_header('Referer', 'https://wx.qq.com/')
        if api == 'webwxgetvoice':
            request.add_header('Range', 'bytes=0-')
        if api == 'webwxgetvideo':
            request.add_header('Range', 'bytes=0-')
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            logging.error('HTTPError = ' + str(e.code))
        except urllib.error.URLError as e:
            logging.error('URLError = ' + str(e.reason))
            print(url)
        except http.client.HTTPException as e:
            logging.error('HTTPException')
        except Exception:
            import traceback
            logging.error('generic exception: ' + traceback.format_exc())
        data=''
        try:
            data = response.read().decode()
        except:
            try:
                data = response.read()
            except:
                logging.debug(url)
        return data

    def _post(self, url, params, jsonfmt= True):
        if jsonfmt:
            data = (json.dumps(params)).encode()

            request = urllib.request.Request(url=url, data=data)
            request.add_header(
                'ContentType', 'application/json; charset=UTF-8')
        else:
            request = urllib.request.Request(url=url, data=urllib.parse.urlencode(params).encode(encoding='utf-8'))

        try:
            response = urllib.request.urlopen(request)
            data = response.read()
            if jsonfmt:
                return json.loads(data.decode('utf-8'))  # object_hook=_decode_dict)
            return data
        except urllib.error.HTTPError as e:
            logging.error('HTTPError = ' + str(e.code))
        except urllib.error.URLError as e:
            logging.error('URLError = ' + str(e.reason))
        except http.client.HTTPException as e:
            logging.error('HTTPException')
        except Exception:
            import traceback
            logging.error('generic exception: ' + traceback.format_exc())

        return ''

    def _tuling(self, info, loc, userid):
        url = 'http://www.tuling123.com/openapi/api'
        try:
            data = {"key": "837712ab905d45bca5ca64c9068c7717",
                    "info": info,
                    "loc": loc,
                    "userid": userid
                    }
            r = json.loads(requests.post(url, data).content.decode())
            if r["code"] == 100000:
                reply = r["text"]
            elif r["code"] == 200000:
                reply = r["text"] + "\n" + r["url"]
            elif r["code"] == 302000:
                reply = r["text"]
                for dic in r["list"]:
                    reply += "\n" + dic["article"] + "\n" + dic["detailurl"]
            elif r["code"] == 308000:
                reply = r["text"]
                for dic in r["list"]:
                    reply += "\n" + dic["article"] + "\n" + dic["info"] + "\n" + dic["detailurl"]
            else:
                reply = r["text"]
                print("图铃机器人返回了未知类型的数据！")
            return reply
        except:
            return "我现在处于未知的深空。。。让我一个人静静 T_T..."

    def _xiaodoubi(self, word):
        url = 'http://www.xiaodoubi.com/bot/chat.php'
        try:
            r = requests.post(url, data={'chat': word}).content
            return r
        except:
            return "让我一个人静静 T_T..."

    def _simsimi(self, word):
        key = ''
        url = 'http://sandbox.api.simsimi.com/request.p?key=%s&lc=ch&ft=0.0&text=%s' % (
            key, word)
        r = requests.get(url)
        ans = r.json()
        if ans['result'] == '100':
            return ans['response']
        else:
            return '你在说什么，风太大听不清列'

    def _searchContent(self, key, content, fmat='attr'):
        if fmat == 'attr':
            pm = re.search(key + '\s?=\s?"([^"<]+)"', content)
            if pm:
                return pm.group(1)
        elif fmat == 'xml':
            pm = re.search('<{0}>([^<]+)</{0}>'.format(key), content)
            if not pm:
                pm = re.search(
                    '<{0}><\!\[CDATA\[(.*?)\]\]></{0}>'.format(key), content)
            if pm:
                return pm.group(1)
        return '未知'

    def find_ava_SyncHost(self):
        SyncHost = [
            'wx2.qq.com',
            'webpush.wx2.qq.com',
            # 'qq.com',
            # 'webpush.wx.qq.com',
            # 'web2.wechat.com',
            # 'webpush.web2.wechat.com',
            # 'wechat.com',
            # 'webpush.web.wechat.com',
            # 'webpush.weixin.qq.com',
            # 'webpush.wechat.com',
            # 'webpush1.wechat.com',
            # 'webpush2.wechat.com',
            # 'webpush.wx.qq.com',
            # 'webpush2.wx.qq.com'
        ]
        for host in SyncHost:
            self.syncHost = host
            try:
                [retcode, selector] = self.synccheck()
                if retcode == '0':
                    self.ava_SynHost_List.append(self.syncHost)
            except:
                print("未知错误：", self.syncHost)
        return len(self.ava_SynHost_List)

class UnicodeStreamFilter:
    def __init__(self, target):
        self.target = target
        self.encoding = 'utf-8'
        self.errors = 'replace'
        self.encode_to = self.target.encoding

    def write(self, s):
        if type(s) == bytes:
            s = s.decode('utf-8')
        s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
        self.target.write(s)

    def flush(self):
        self.target.flush()

if sys.stdout.encoding == 'cp936':
    sys.stdout = UnicodeStreamFilter(sys.stdout)

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    if not sys.platform.startswith('win'):
        import coloredlogs

        coloredlogs.install(level='DEBUG')

    webwx = WebWeixin()

    webwx.start()
