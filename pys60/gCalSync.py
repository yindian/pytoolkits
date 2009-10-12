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
'''
Upload the appointments or events for a day to Google Calendar
based on the example:
http://www.thisismobility.com/software/google_cal_sample.txt
'''
import socket
import httplib, urllib, urlparse
from time import *
import e32calendar as calendar
import appuifw
socket.setdefaulttimeout(15)

def GoogleAuth(u, p):
    params = urllib.urlencode({'Email':u,'Passwd':p,'service':'cl',
                               'source':'pyGCalSync'})
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = httplib.HTTPSConnection("www.google.com")
    conn.request("POST", "/accounts/ClientLogin", params, headers)
    response = conn.getresponse()
    body = response.read()
    conn.close()
    vals = dict([x.split('=') for x in body.splitlines()]) 
    return vals['Auth']

def SessionUrl( auth, url ):
    headers = {"Accept": "text/plain",
               'Authorization':'GoogleLogin auth='+auth}
    conn = httplib.HTTPConnection("www.google.com")
    conn.request("GET", url, None, headers)
    response = conn.getresponse()
    sessionurl = response.getheader('Location')
    parts = urlparse.urlsplit(sessionurl)
    return parts[2] + '?' + parts[3]

def dictFromS60Event(event):
    title = event.content
    descr = ''
    where = event.location
    start = strftime('%Y-%m-%dT%H:%M:%SZ', gmtime(event.start_time))
    end = strftime('%Y-%m-%dT%H:%M:%SZ', gmtime(event.end_time))
    return {'title':title,'descr':descr,'where':where,'start':start,'end':end}


def atomEntryFromDict(u,p,n,d):
    entry = """
<entry xmlns='http://www.w3.org/2005/Atom'
    xmlns:gd='http://schemas.google.com/g/2005'>
  <category scheme='http://schemas.google.com/g/2005#kind'
    term='http://schemas.google.com/g/2005#event'></category>
  <title type='text'>%s</title>
  <content type='text'>%s</content>
  <author>
    <name>%s</name>
    <email>%s</email>
  </author>
  <gd:transparency
    value='http://schemas.google.com/g/2005#event.opaque'>
  </gd:transparency>
  <gd:eventStatus
    value='http://schemas.google.com/g/2005#event.confirmed'>
  </gd:eventStatus>
  <gd:where valueString='%s'></gd:where>
  <gd:when startTime='%s'
     endTime= '%s'>
  </gd:when>
</entry> """ % (d['title'],d['descr'], n, u, d['where'],d['start'],d['end'])
    return entry

def insertGcal(atomEntry,sessionUrl,auth):
    headers = {'Content-Type': 'application/atom+xml',
               'Authorization': 'GoogleLogin auth='+auth} 
    conn = httplib.HTTPConnection("www.google.com")
    conn.request("POST", sessionUrl, atomEntry, headers)
    response = conn.getresponse()
    body = response.read()
    conn.close()

def main():
    syncday = appuifw.query(u"The date to be uploaded",u"date",time())
    if syncday is None:
        appuifw.note(u"User Cancelled")
        return
    cal = calendar.open()
    entries = cal.daily_instances(syncday,appointments=1,events=1)
    if len(entries)>0:
        ap_names = []
        ap_list_of_dicts = socket.access_points()
        for item in ap_list_of_dicts:
            ap_names.append(item['name'])
        ap_offset = appuifw.popup_menu(ap_names, u"Select default access point")
        if ap_offset is None:
        	appuifw.note(u"Cancelled!")
        	return
        socket.set_default_access_point(ap_names[ap_offset])
        u=appuifw.query(u'email','text',u"@gmail.com")
        p=appuifw.query(u'password','code',u"")
        n=appuifw.query(u'username','text',u"")
        if u is None or p is None or n is None:
            appuifw.note(u"User Cancelled")
            return
        u=u.encode("utf8")
        p=p.encode("utf8")
        n=n.encode("utf8")
        feedloc = '/calendar/feeds/'+u+'/private/full'
        auth = GoogleAuth( u, p )
        sess = SessionUrl( auth, feedloc )
        for entry in entries:
            event = cal[entry['id']]
            dict = dictFromS60Event(event)
            entry = atomEntryFromDict(u,p,n,dict)
            entry=entry.encode("utf8")
            insertGcal(entry,sess,auth)
            print "Added : " + event.content

if __name__=="__main__":
    main()