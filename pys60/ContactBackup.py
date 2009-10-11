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
Backup the Contacts of a Symbian to the s60spot
'''

HOSTNAME=""
POSTURL=""
USERNAME=""
PASSWORD=""
EncrptyKey=""

import httplib, mimetypes
import socket
socket.setdefaulttimeout(15)

def post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTPConnection(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    resp=h.getresponse()
    return resp

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

import contacts
import pickle
import appuifw

def getContactsData():
	db = contacts.open()
	all=[]
	for id in db:
		s60contact=db[id]
		first_name=""
		last_name=""
		phonenum=""
		try:
			first_name=s60contact.find(type="first_name")[0].value
		except:
			pass
		try:
			last_name=s60contact.find(type="last_name")[0].value
		except:
			pass
		try:
			phonenum=s60contact.find(type="mobile_number")[0].value
		except:
			pass
		all.append((first_name, last_name, phonenum))
	return pickle.dumps(all)

def UploadData(data):
	postdata=[]
	postdata.append(("contact", "conctact.db", data))
	resp = post_multipart(HOSTNAME, POSTURL, [], postdata)
	if resp.status == 200:
		return True
	else:
		return False

def main():
	data = getContactsData()
	ap_names = []
	ap_list_of_dicts = socket.access_points()
	for item in ap_list_of_dicts:
		ap_names.append(item['name'])
	ap_offset = appuifw.popup_menu(ap_names, u"Select default access point")
	if ap_offset is None:
		appuifw.note(u"Cancelled")
		return
	socket.set_default_access_point(ap_names[ap_offset])
	status=UploadData(data)
	if status:
		appuifw.note(u"Backup Successfully")
	else:
		appuifw.note(u"Failed, unknown error")

if __name__=="__main__":
	main()