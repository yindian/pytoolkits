#!/usr/bin/python
# -*- coding:UTF-8 -*-
'''
Copyright 2009 http://code.google.com/p/pytoolkits/. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:
  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above
    copyright notice, this list of conditions and the following
    disclaimer in the documentation and/or other materials provided
    with the distribution.
  * Neither the name of http://code.google.com/p/pytoolkits/ nor the names of its
    contributors may be used to endorse or promote products derived
    from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import cookielib
import urllib2
import urllib
import re
import os
import pickle

class PasswordManger(object):
	def __init__(self):
		self.regpath = "Software\\pyIPGW"
		self.conffile = "/.pyipgw.conf"
		self.username = ""
		self.password = ""
		
	def getinfo(self):
		try:
			import _winreg
			hkey = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, self.regpath)
			if hkey:
				username, type = _winreg.QueryValueEx(hkey, "username")
				password, type = _winreg.QueryValueEx(hkey, "password")
				return username, password
		except:
			try:
				path = os.environ['HOME']+self.conffile
				string = open(path).read()
				pwm = pickle.loads(string)
				return pwm.username, pwm.password
			except:
				raise Exception("Can not get username and password")

	def setinfo(self, username, password):
		try:
			import _winreg
			hkey = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, self.regpath)
			if hkey:
				_winreg.SetValueEx(hkey,"username", 0, _winreg.REG_SZ, username)
				_winreg.SetValueEx(hkey,"password", 0, _winreg.REG_SZ, password)
		except:
			try:
				path = os.environ['HOME']+self.conffile
				self.username = username
				self.password = password
				string = pickle.dump(self, open(path,"w"))
			except:
				raise Exception("Can not save useranme and password")

class IPGWClient(object):
	def __init__(self, passwdm):
		self.cj = cookielib.CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		self.magicString = "|;kiDrqvfi7d$v0p5Fg72Vwbv2;|"
		self.infopattern = re.compile(r'<!--IPGWCLIENT_START (.*) IPGWCLIENT_END-->')
		self.username = ""
		self.password = ""
		self.passwdm = passwdm
		self.logged = False
		
	def open(self):
		self.username, self.password=self.passwdm.getinfo()
		
	def close(self):
		self.passwdm.setinfo(self.username, self.password)
		
	def setinfo(self, username, passwd):
		self.username, self.password=username, passwd
		
	def doConnect(self, free=True):
		if not self.logged:
			self.__login()
		self.doDisconnect()
		if free:
			resp = self.opener.open("https://its.pku.edu.cn/netportal/ipgwopen")
		else:
			resp = self.opener.open("https://its.pku.edu.cn/netportal/ipgwopenall")
		content = resp.read()
		info = self.infopattern.search(content).group(1)
		return self.__parse(info)

	def doDisconnect(self, all = True):
		if not self.logged:
			self.__login()
		if all:
			resp = self.opener.open("https://its.pku.edu.cn/netportal/ipgwcloseall")
		else:
			resp = self.opener.open("https://its.pku.edu.cn/netportal/ipgwclose")
		content = resp.read()
		info = self.infopattern.search(content).group(1)
		return self.__parse(info)

	def __parse(self, info):
		ret=''
		info = info.strip()
		for item in info.split(' '):
			item = item.split('=')
			if len(item) == 1:
				item.append("")
			ret += "%15s: %s\n" % (item[0], item[1])
		return ret

	def __login(self):
		self.logged = False
		resp = self.opener.open("https://its.pku.edu.cn/cas/login")
		info = resp.read()
		data = {}
		ltpattern = re.compile(r'name="lt" value="([^"]+)"')
		data['lt'] = ltpattern.search(info).group(1)
		data['username1'] = self.username
		data['password'] = self.password
		data['_currentStateId'] = 'viewLoginForm'
		data['_eventId'] = 'submit'
		data['username'] = self.username+self.magicString+self.password+self.magicString+'2'
		querystring = urllib.urlencode(data)
		resp = self.opener.open("https://its.pku.edu.cn/cas/login",querystring)
		content = resp.read()
		if content.find('Username or Password error!') != -1:
			raise Exception("Username or Password error")
		resp = self.opener.open("https://its.pku.edu.cn/netportal/")
		resp.read()
		self.logged = True

import wx

class IPGWDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE,
            useMetal=False,
            ):
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)
        sizer = wx.BoxSizer(wx.VERTICAL)
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "username:")
        label.SetHelpText("")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.username = wx.TextCtrl(self, -1, "", size=(80,-1))
        self.username.SetHelpText("username")
        box.Add(self.username, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "password:")
        label.SetHelpText("")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.password = wx.TextCtrl(self, -1, "", size=(80,-1), style=wx.TE_PASSWORD)
        self.password.SetHelpText("password")
        box.Add(self.password, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_OK)
        btn.SetHelpText("")
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetHelpText("")
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.SetSizer(sizer)
        sizer.Fit(self)

from wx.lib.wordwrap import wordwrap

class wxIPGWApp(wx.App):
    def OnInit(self):
        try:
            client=IPGWClient(PasswordManger())
            try:
            	client.open()
            except Exception,e:
            	pass
            dlg = IPGWDialog(None, -1, "PKU IP Gateway")
            dlg.username.SetValue(client.username)
            dlg.password.SetValue(client.password)
            dlg.CenterOnScreen()
            val = dlg.ShowModal()
            if val == wx.ID_OK:
              client.setinfo(dlg.username.GetValue(), dlg.password.GetValue())
              ret=client.doConnect()
              info=wx.AboutDialogInfo()
              info.Name="wxIPGW"
              info.Version="0.1"
              info.Copyright=""
              info.Description=wordwrap(ret,350, wx.ClientDC(dlg))
              info.WebSite=("","")
              info.Developers=[]
              wx.AboutBox(info)
              try:
              	client.close()
              except Exception,e:
              	pass
            dlg.Destroy()
            return True
        except Exception,e:
            info = wx.AboutDialogInfo()
            info.Name = "error"
            info.Description=str(e)
            wx.AboutBox(info)
            return False

if __name__=="__main__":
	app = wxIPGWApp(0)
	app.MainLoop()
