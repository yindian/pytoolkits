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

from _winreg import *
import ctypes
import time
def getInstallTime():
	datepath = "Software\\Microsoft\\Windows NT\\CurrentVersion"
	datepath2 = "Software\\Microsoft\\Windows\\CurrentVersion"
	try:
		key = OpenKey(HKEY_LOCAL_MACHINE, datepath)
		when,type = QueryValueEx(key, "InstallDate")
		installtime = time.strftime("%z %Y-%m-%d %X %A",time.localtime(when))
		return installtime
	except WindowsError:
		try:
			key=OpenKey(HKEY_LOCAL_MACHINE,datepath2)
			when,type=QueryValueEx(key, "FirstInstallDate")
			installtime=time.strftime("%z %Y-%m-%d %X %A",time.localtime(when))
			return installtime
		except WindowsError:
			raise Exception("Can not read install time")

def FormatSeconds(sec):
    sec /= 1000
    min = sec/60
    sec %= 60
    hour = min/60
    min %= 60
    return "%d hours %d minutes %d seconds" %( hour,min,sec)
   
def main():
	MessageBox = ctypes.windll.user32.MessageBoxA
	installtime = getInstallTime()
	sec=ctypes.windll.kernel32.GetTickCount()
	installtime +="\n Running "+FormatSeconds(sec)
	MessageBox(0,installtime,"Install Time",0)
	
if __name__ == "__main__":
	main()