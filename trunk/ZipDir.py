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

import zipfile
import os
import pickle

class ZipDir(object):
	def __init__(self,name,destdir):
		self.dirname=name
		self.destdir=destdir
		self.filelist=[]
		self.FILESIZELIMIT=1000000
		
	def getFileList(self):
		self.filelist=[]
		self.TraverseDir(self.dirname)
		return self.filelist
	
	def TraverseDir(self,dir):
		for (dirpath,dirnames,filenames) in os.walk(dir):
			for filename in filenames:
				self.filelist.append(os.path.join(dirpath,filename))
	
	def dumpzip(self):
		filelist=self.getFileList()
		bookindex={}
		index=0
		zipname="%s%d.zip"%(self.destdir,index)
		result=zipfile.ZipFile(zipname, "w")
		size=0
		for f in zipdir.filelist:
			st=os.lstat(f)
			if st.st_size+size < self.FILESIZELIMIT:
				arc=f.replace(self.dirname, "")
				arc=arc.split(os.sep)
				arc="/".join(arc)
				result.write(f,arc)
				bookindex[arc]=index
				size+=st.st_size
			else:
				result.close()
				index+=1
				zipname="%s%d.zip"%(self.destdir,index)
				result=zipfile.ZipFile(zipname, "w")
				size=0
		result.close()
		indexname="%sbookindex"%self.destdir
		pickle.dump(bookindex, open(indexname,"wb"))
		
if __name__=="__main__":
	DirName="G:\\standardlib\\"
	DestName="G:\\"
	zipdir=ZipDir(DirName,DestName)
	zipdir.dumpzip()
