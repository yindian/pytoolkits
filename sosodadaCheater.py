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
"""
增加  http://www.sosodadada.com积分的程序

Last Update: Dec 11, 2009 

"""

import cookielib
import urllib2
import urllib
import re

class sosodadaCheater(object):
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.cj = cookielib.CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		self.host = "http://www.sosodada.com"
		self.loginurl = "/ULogin.aspx"
		self.questurl = "/Print_Member/Questions.aspx"
		self.infourl = "/Print_Member/DefaultInfo.aspx"
		self.logouturl = ""
		
	def Login(self):
		data = {}
		resp = self.opener.open(self.host + self.loginurl)
		info = resp.read()
		ltpattern = re.compile(r'id="__VIEWSTATE" value="([^"]+)"')
		data['__VIEWSTATE'] = ltpattern.search(info).group(1)
		ltpattern = re.compile(r'id="__EVENTVALIDATION" value="([^"]+)"')
		data['__EVENTVALIDATION'] = ltpattern.search(info).group(1)
		data["ctl00$ContentPlaceHolder1$txtUserName"] = self.username
		data["ctl00$ContentPlaceHolder1$txtUserPwd"] = self.password
		data["ctl00$ContentPlaceHolder1$imgbtnLogin.x"] = "15"
		data["ctl00$ContentPlaceHolder1$imgbtnLogin.y"] = "13"
		data["__EVENTARGUMENT"] = ""
		data["__EVENTTARGET"] = ""
		querystring = urllib.urlencode(data)
		resp = self.opener.open(self.host + self.loginurl, querystring)
		content = resp.read()
		return content
	
	def SkipQuestions(self, content = None):
		data = {}
		urlpattern = re.compile(r'method="post" action="([^"]+)"')
		action = urlpattern.search(content).group(1)
		ltpattern = re.compile(r'id="__VIEWSTATE" value="([^"]+)"')
		data['__VIEWSTATE'] = ltpattern.search(content).group(1)
		ltpattern = re.compile(r'id="__EVENTVALIDATION" value="([^"]+)"')
		data['__EVENTVALIDATION'] = ltpattern.search(content).group(1)
		data["imgbtnNext.x"] = "28"
		data["imgbtnNext.y"] = "18"
		querystring = urllib.urlencode(data)
		resp = self.opener.open(self.host + "/"+ action, querystring)
		content = resp.read()
		return content
	
	def WinScore(self, content = None):
		data = {}
		ltpattern = re.compile(r'id="__VIEWSTATE" value="([^"]+)"')
		data['__VIEWSTATE'] = ltpattern.search(content).group(1)
		ltpattern = re.compile(r'id="__EVENTVALIDATION" value="([^"]+)"')
		data['__EVENTVALIDATION'] = ltpattern.search(content).group(1)
		data["__EVENTARGUMENT"] = ""
		data["__EVENTTARGET"] = ""
		data["ctl00$ContentPlaceHolder1$btnGetScores"] = "领取积分"
		querystring = urllib.urlencode(data)
		resp = self.opener.open(self.host + self.infourl, querystring)
		content = resp.read()
		return content
	
	def PrintScore(self, content):
		pattern = re.compile(r'<span id=".*?"><i><font face=".*?" color=".*?" size=".*?">(.*?)</font></i></span>')
		print pattern.search(content).group(1)
		pattern = re.compile(r'<div id="ctl00_ContentPlaceHolder1_GetScores" style="width: 332px; text-align: center;">(.*?)</div>')
		print pattern.search(content).group(1)

if __name__ == "__main__":
	cheater = sosodadaCheater("", "")
	content = cheater.Login()
	content = cheater.SkipQuestions(content)
	content = cheater.WinScore(content)
	cheater.PrintScore(content)
