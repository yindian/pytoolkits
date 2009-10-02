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
import socket
import cookielib
import urllib2
import urllib
import re
import appuifw
socket.setdefaulttimeout(15)

class PasswordManger(object):
	def __init__(self):
		self.filename="pyipgw.conf"
		self.username=""
		self.password=""
	def getinfo(self):
		try:
			FILE = open(self.filename, 'r')
			self.username = FILE.readline()
			self.username = self.username.strip('\n')
			self.password = FILE.readline()
			self.password = self.password.strip('\n')
			FILE.close()
			return self.username,self.password
		except:
			pass
		self.username = appuifw.query(u'username','text')
		if not self.username:
			return False
		self.password = appuifw.query(u'password','code')
		if not self.password:
			return False
		try:
			FILE = open(self.filename, 'w')
			FILE.write(self.username)
			FILE.write("\n")
			FILE.write(self.password)
			FILE.close()
		except:
			pass
		return self.username,self.password		
	
	def setinfo(self,username,password):
		pass
	
class IPGWClient(object):
	def __init__(self, passwdm):
		self.cj=cookielib.CookieJar()
		self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		self.magicString="|;kiDrqvfi7d$v0p5Fg72Vwbv2;|"
		self.infopattern=re.compile(r'<!--IPGWCLIENT_START (.*) IPGWCLIENT_END-->')
		self.username=""
		self.password=""
		self.passwdm=passwdm
		self.logged=False
		
	def open(self):
		ret = self.passwdm.getinfo()
		if not ret:
			return False
		self.username,self.password = ret
		return True
		
	def close(self):
		self.passwdm.setinfo(self.username,self.password)
		
	def setinfo(self,username,passwd):
		self.username,self.password=username,passwd
		
	def doConnect(self, free=True):
		if not self.logged:
			self.__login()
		self.doDisconnect()
		if free:
			resp=self.opener.open("https://its.pku.edu.cn/netportal/ipgwopen")
		else:
			resp=self.opener.open("https://its.pku.edu.cn/netportal/ipgwopenall")
		content=resp.read()
		info=self.infopattern.search(content).group(1)
		return self.__parse(info)

	def doDisconnect(self, all = True):
		if not self.logged:
			self.__login()
		if all:
			resp=self.opener.open("https://its.pku.edu.cn/netportal/ipgwcloseall")
		else:
			resp=self.opener.open("https://its.pku.edu.cn/netportal/ipgwclose")
		content=resp.read()
		info=self.infopattern.search(content).group(1)
		return self.__parse(info)

	def __parse(self, info):
		ret=''
		retDict={}
		info=info.strip()
		for item in info.split(' '):
			item = item.split('=')
			if len(item) == 1:
				item.append("")
			retDict[item[0]] = item[1]
			ret += "%15s: %s\n" % (item[0], item[1])
		return ret

	def __login(self):
		self.logged=False
		resp=self.opener.open("https://its.pku.edu.cn/cas/login")
		info=resp.read()
		data={}
		ltR = re.compile(r'name="lt" value="([^"]+)"')
		lN = ltR.search(info)
		data['lt'] = lN.group(1)
		data['username1']=self.username
		data['password']=self.password
		data['_currentStateId']='viewLoginForm'
		data['_eventId']='submit'
		data['username']=self.username+self.magicString+self.password+self.magicString+'2'
		querystring = urllib.urlencode(data)
		resp = self.opener.open("https://its.pku.edu.cn/cas/login",querystring)
		content = resp.read()
		if content.find('Username or Password error!') != -1:
			raise Exception("Username or Password error")
		resp=self.opener.open("https://its.pku.edu.cn/netportal/")
		resp.read()
		self.logged=True

def main():
	ap_names = []
	ap_list_of_dicts = socket.access_points()
	for item in ap_list_of_dicts:
		ap_names.append(item['name'])
	ap_offset = appuifw.popup_menu(ap_names, u"Select default access point")
	if ap_offset is None:
		appuifw.note(u"Cancelled!")
	else:
		socket.set_default_access_point(ap_names[ap_offset])
		client=IPGWClient(PasswordManger())
		try:
			if not client.open():
				appuifw.note(u"Cancelled!")
				return
			ret = client.doConnect()
			appuifw.note(ret.decode("utf8"))
			print ret
		except Exception,e:
			print e
			appuifw.note(u"Cancelled!")

if __name__=="__main__":
	main()