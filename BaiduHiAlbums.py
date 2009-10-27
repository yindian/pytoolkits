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

import re
import sys 
import time
import urllib
import urllib2
import logging
import os

class ImagePersistence(object):
	def __init__(self, downloader):
		"""
		downloader: a HiBaiduAlbumDownloader instance
		"""
		self.downloader=downloader
		self.destdir="g:\\album"
		self.logger=None
	
	def getlogger():
		logger = logging.getLogger()
		hdlr = logging.FileHandler("log.log")
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		hdlr.setFormatter(formatter)
		logger.addHandler(hdlr)
		logger.setLevel(logging.NOTSET)
		return logger
	
	def init(self):
		destpath=self.destdir+os.sep+urllib.unquote(self.downloader.username)
		if not os.path.exists(destpath):
			os.makedirs(destpath)
	
	def persistence(self, album, image):
		"""
			album: the name of the album to be persisted.
			images: a tuple: (filename, image_data)
		"""
		destdir=self.destdir+os.sep+urllib.unquote(self.downloader.username)+os.sep+urllib.unquote(album)
		if not os.path.exists(destdir):
			os.makedirs(destdir)
		file=open(destdir+os.sep+image[0],"wb")
		file.write(image[1])
		file.close()
   
class HiBaiduAlbumDownloader(object):
	"""
	"""
	def __init__(self, user=None):
		"""
		username:
		persistencer: a ImagePersistence instance 
		"""
		self.username=user
		self.persistencer=None
	
	def setPersistence(self, p):
		self.persistencer=p
		self.persistencer.init()

	def getAlbumNames(self):
		patt=re.compile("""imgarr\[len\]={purl:"/%s/album/(.+?)","""%(self.username))
		ret=[]
		i=0
		cont=True
		while cont:
			cont=False
			albumpath="http://hi.baidu.com/%s/album/index/%d"%(self.username,i)
			i+=1
			try:
				req=urllib2.Request(albumpath)
				resp=urllib2.urlopen(req)
				content=resp.read()
				m=patt.findall(content)
				for r in m:
					cont=True
					ret.append(r)
			except urllib2.HTTPError,e:
				print "Http Error",e.code
				retry=True
			except urllib2.URLError,e:
				print "Url Error",e.reason
				retry=True
			except Exception,e:
				print e
		return ret
	
	def getImages(self,albumname):
		patt=re.compile("""imgarr\[len\]={purl:"/%s/album/item/(.+?).html","""%(self.username))
		default_header={"Accept":"*/*",
                "Host":"hiphotos.baidu.com",
                "Referer":"http://hi.baidu.com/%s/blog"%(self.username),
                "Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1;OfficeLiveConnector.1.2)"
                }
		imageid=[]
		i=0
		cont=True
		while cont:
			time.sleep(1)
			cont=False
			retry=True
			while retry:
				retry=False
				try:
					indexi="http://hi.baidu.com%s/index/%d"%(albumname,i)
					i+=1
					sys.stderr.write("/%s/album/.+?/index/%d\n"%(self.username,i))
					nextpatt=re.compile("/%s/album/.+?/index/%d"%(self.username,i))
					req=urllib2.Request(indexi)
					ret=urllib2.urlopen(req)
					content=ret.read()
					if nextpatt.search(content):
						cont=True
					mat=patt.findall(content)
					for m in mat:
						imageid.append(m)
				except urllib2.HTTPError,e:
					print "Http Error",e.code
					retry=True
				except urllib2.URLError,e:
					print "Url Error",e.reason
					retry=True
				except Exception,e:
					print e
		print len(imageid)
		for img in imageid:
			retry=True
			while retry:
				time.sleep(1)
				retry=False
				picurl="http://hiphotos.baidu.com/%s/pic/item/%s.jpg"%(self.username,img)
				try:
					req=urllib2.Request(picurl,headers=default_header)
					ret=urllib2.urlopen(req)
					content_length=ret.info().get("Content-Length")
					data=ret.read()
					self.persistencer.persistence(albumname,("%s.jpg"%img,data))
				except urllib2.HTTPError,e:
					print "Http Error",e.code
					retry=True
				except urllib2.URLError,e:
					print "Url Error",e.reason
					retry=True
				except Exception,e:
					print e
	def download(self):
		albums=self.getAlbumNames()
		if self.logger:
			self.logger.info("All %d albums",len(albums))
		for album in albums:
			if self.logger:
				self.logger.info("Getting %s"%urllib.unquote(album))
			self.getImages(album)
			 
if __name__=="__main__":
	username=""
	downloader=HiBaiduAlbumDownloader(username)
	per=ImagePersistence(downloader)
	per.init()
	downloader.setPersistence(per)
	downloader.download()
	