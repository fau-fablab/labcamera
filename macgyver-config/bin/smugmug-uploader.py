#!/usr/bin/python
 
##########
# Requirements: Python 2.6 or
#               simplejson from http://pypi.python.org/pypi/simplejson
##########
 
EMAIL='julian.hammer@fablab.fau.de'
PASSWORD='rF4YDiFw0a'
 
##########
APIKEY='zoqsn0u3oPqh270HfHP3mDwh46AOvdHe'
API_VERSION='1.2.2'
API_URL='https://api.smugmug.com/services/api/json/1.2.2/'
UPLOAD_URL='http://upload.smugmug.com/photos/xmlrawadd.mg'
 
import sys, re, urllib, urllib2, urlparse, hashlib, traceback, os.path
try    : import json
except : import simplejson as json
 
if len(sys.argv) < 3 :
  print 'Usage:'
  print '  upload.py  album  picture1  [picture2  [...]]'
  print
  sys.exit(0)
 
album_name = sys.argv[1]
su_cookie  = None
 
def safe_geturl(request) :
  global su_cookie
 
  # Try up to three times
  for x in range(5) :
    try :
      response_obj = urllib2.urlopen(request)
      response = response_obj.read()
      result = json.loads(response)
 
      # Test for presence of _su cookie and consume it
      meta_info = response_obj.info()
      if meta_info.has_key('set-cookie') :
        match = re.search('(_su=\S+);', meta_info['set-cookie'])
        if match and match.group(1) != "_su=deleted" :
          su_cookie = match.group(1)
      if result['stat'] != 'ok' : raise Exception('Bad result code')
      return result
    except :
      if x < 4 :
        print "  ... failed, retrying"
      else :
        print "  ... failed, giving up"
        print "  Request was:"
        print "  " + request.get_full_url()
        try :
          print "  Response was:"
          print response
        except :
          pass
        traceback.print_exc()
        #sys.stdin.readline()
        #sys.exit(1)
        return result
 
def smugmug_request(method, params) :
  global su_cookie
 
  paramstrings = [urllib.quote(key)+'='+urllib.quote(params[key]) for key in params]
  paramstrings += ['method=' + method]
  url = urlparse.urljoin(API_URL, '?' + '&'.join(paramstrings))
  request = urllib2.Request(url)
  if su_cookie :
    request.add_header('Cookie', su_cookie)
  return safe_geturl(request)
 
result = smugmug_request('smugmug.login.withPassword',
                         {'APIKey'       : APIKEY,
                          'EmailAddress' : EMAIL,
                          'Password'     : PASSWORD})
session = result['Login']['Session']['id']
 
result = smugmug_request('smugmug.albums.get', {'SessionID' : session})
album_id = None
for album in result['Albums'] :
  if album['Title'] == album_name :
    album_id = album['id']
    break
if album_id is None :
  print 'That album does not exist'
  sys.exit(1)
 
for filename in sys.argv[2:] :
  data = open(filename, 'rb').read()
  print 'Uploading ' + filename
  upload_request = urllib2.Request(UPLOAD_URL,
                                   data,
                                   {'Content-Length'  : len(data),
                                    'Content-MD5'     : hashlib.md5(data).hexdigest(),
                                    'Content-Type'    : 'none',
                                    'X-Smug-SessionID': session,
                                    'X-Smug-Version'  : API_VERSION,
                                    'X-Smug-ResponseType' : 'JSON',
                                    'X-Smug-AlbumID'  : album_id,
                                    'X-Smug-FileName' : os.path.basename(filename) })
  result = safe_geturl(upload_request)
  if result['stat'] == 'ok' :
    print "  ... successful"
 
print 'Done'
# sys.stdin.readline()
