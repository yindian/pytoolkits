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
import time
import datetime
import appuifw
import e32

def diffDate():
	fromday = appuifw.query(u"Start Day",u"date",time.time())
	endday = appuifw.query(u"End Day",u"date",time.time())
	if not fromday:
		fromday=time.time()
	if not endday:
		endday=time.time()
	beg=datetime.date.fromtimestamp(fromday)
	end=datetime.date.fromtimestamp(endday)
	td=end-beg
	days=td.days
	fromDay=beg.isoformat()
	toDay=end.isoformat()
	appuifw.note(u"From %s to %s is %s days"%(fromDay,toDay,days))

def addDays():
	baseday = appuifw.query(u"Start Day",u"date",time.time())
	days = appuifw.query(u"Add Day",u"number")
	if not baseday:
		baseday = time.time()
	if not days:
		days = 0
	td = datetime.timedelta(days=days)
	baseday = datetime.date.fromtimestamp(baseday)
	result = baseday + td
	fromDay = baseday.isoformat()
	resultDay = result.isoformat()
	appuifw.note(u"After %d days from %s is %s"%(days, fromDay, resultDay))

def subDays():
	baseday = appuifw.query(u"Start Day",u"date",time.time())
	days = appuifw.query(u"Add Day",u"number")
	if not baseday:
		baseday = time.time()
	if not days:
		days = 0
	td = datetime.timedelta(days=days)
	baseday = datetime.date.fromtimestamp(baseday)
	result = baseday + td
	fromDay = baseday.isoformat()
	resultDay = result.isoformat()
	appuifw.note(u"Before %d days of %s is %s"%(days, fromDay, resultDay))

def exit_key_handler():
	app_lock.signal()

if __name__=="__main__":
	appuifw.app.menu = [
					(u"Diff Date", diffDate),
					(u"Add Days", addDays),
					(u"Sub Days", subDays)
					]
	app_lock = e32.Ao_lock()
	appuifw.app.exit_key_handler = exit_key_handler
	app_lock.wait()
