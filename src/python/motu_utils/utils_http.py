#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python motu client
#
# Motu, a high efficient, robust and Standard compliant Web Server for Geographic
#  Data Dissemination.
# 
#  http://cls-motu.sourceforge.net/
# 
#  (C) Copyright 2009-2010, by CLS (Collecte Localisation Satellites) -
#  http://www.cls.fr - and Contributors
# 
# 
#  This library is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.
# 
#  This library is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#  or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
#  License for more details.
# 
#  You should have received a copy of the GNU Lesser General Public License
#  along with this library; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import sys


if sys.version_info > (3, 0):
    import urllib.request, urllib.error
    from urllib.request import HTTPCookieProcessor, Request
    from urllib.request import HTTPSHandler, HTTPHandler, install_opener, build_opener, \
        HTTPRedirectHandler, ProxyHandler, HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm
    from urllib.request import HTTPErrorProcessor as HTTPErrorProcessor_
    from http.client import HTTPConnection, HTTPSConnection
    from http.cookiejar import CookieJar
else:
    from httplib import HTTPConnection, HTTPSConnection
    from urllib2 import HTTPSHandler, install_opener, build_opener, \
    HTTPRedirectHandler, HTTPRedirectHandler, ProxyHandler, HTTPBasicAuthHandler, \
    HTTPPasswordMgrWithDefaultRealm, HTTPCookieProcessor, HTTPSHandler, HTTPHandler, Request
    from urllib2 import HTTPErrorProcessor as HTTPErrorProcessor_
    from cookielib import CookieJar

from motu_utils import utils_log
import logging
import ssl
import socket


class TLS1v2Connection(HTTPSConnection):
    """Like HTTPSConnection but more specific"""
    def __init__(self, host, **kwargs):
        HTTPSConnection.__init__(self, host, **kwargs)
 
    def connect(self):
        """Overrides HTTPSConnection.connect to specify TLS version"""
        # Standard implementation from HTTPSConnection, which is not
        # designed for extension, unfortunately
        sock = socket.create_connection((self.host, self.port),
                self.timeout, self.source_address)
        if getattr(self, '_tunnel_host', None):
            self.sock = sock
            self._tunnel()
 
        # This is the only difference; default wrap_socket uses SSLv23
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                ssl_version=ssl.PROTOCOL_TLSv1_2)
 
class TLS1v2Handler(HTTPSHandler):
    """Like HTTPSHandler but more specific"""
    def __init__(self):
        HTTPSHandler.__init__(self)
 
    def https_open(self, req):
        return self.do_open(TLS1v2Connection, req)

# Overide default handler
install_opener(build_opener(TLS1v2Handler()))


class HTTPErrorProcessor(HTTPErrorProcessor_):
    def https_response(self, request, response):
        # Consider error codes that are not 2xx (201 is an acceptable response)
        code, msg, hdrs = response.code, response.msg, response.info()
        if code >= 300:
            response = self.parent.error('http', request, response, code, msg, hdrs)
        return response
    

class SmartRedirectHandler(HTTPRedirectHandler):

    def http_error_302(self, req, fp, code, msg, headers):
        result = HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)              
        result.status = code                                
        return result
    
    
def open_url(url, **kargsParam):
    """open an url and return an handler on it.
       arguments can be :
         headers : http headers to send
            headers = {"Accept": "text/plain", 
                       "User-Agent": "a user agent"
                      }
                      
         proxy : the proxy to use when connecting to the url
            proxy = { "url": "http://aproxy.server",
                      "port": 8080,
                      "user": "username",
                      "password": "userpassword"
                    }
          
         authentication: the authentication information
            authentication = { "mode": "basic",
                               "user": "username",
                               "password": "password" }
    """   
    data = None
    log = logging.getLogger("utils_http:open_url")
    kargs = kargsParam.copy()
    # common handlers
    handlers = [SmartRedirectHandler(),
                HTTPCookieProcessor(CookieJar()),
                HTTPHandler(),
                TLS1v2Handler(),
                utils_log.HTTPDebugProcessor(log),
                HTTPErrorProcessor()
                ]

    # add handlers for managing proxy credentials if necessary        
    if 'proxy' in kargs:
        urlProxy = ''
        if 'user' in kargs['proxy']:
            urlProxy = kargs['proxy']['user'] + ':' + kargs['proxy']['password'] + '@'

        urlProxy += kargs['proxy']['netloc'] 

        handlers.append( ProxyHandler({'http':urlProxy, 'https':urlProxy}) )
        handlers.append( HTTPBasicAuthHandler() )
        
        del kargs['proxy']
        
    if 'authentication' in kargs:
        # create the password manager
        #password_mgr = HTTPPasswordMgrWithDefaultRealm(ssl_version=ssl.PROTOCOL_TLSv1)
        password_mgr = HTTPPasswordMgrWithDefaultRealm()
        urlPart = url.partition('?')
        password_mgr.add_password(None, urlPart, kargs['authentication']['user'], kargs['authentication']['password'])
        # add the basic authentication handler
        handlers.append(HTTPSHandler(password_mgr))
        del kargs['authentication']
    
    if 'data' in kargs:
        data = kargs['data']
        del kargs['data']
    
    _opener = build_opener(*handlers)
    log.log(utils_log.TRACE_LEVEL, 'list of handlers:')
    for h in _opener.handlers:
        log.log(utils_log.TRACE_LEVEL, ' . %s', str(h))

    # create the request
    if( data != None ):
        r = Request(url, data, **kargs)
    else:
        r = Request(url, **kargs)

    # open the url, but let the exception propagates to the caller  
    return _opener.open(r)


def encodeValue(v):
  return str(v).replace('#','%23').replace(' ','%20')

def encode(options):    
    opts = []
    for k, vset in options.dict().items():
        for v in vset:
            if type(v) in (tuple, list):
                for v2 in v:
                   opts.append('%s=%s' % (str(k), encodeValue(v2)))
            else:
                opts.append('%s=%s' % (str(k), encodeValue(v)))
    return '&'.join(opts)
