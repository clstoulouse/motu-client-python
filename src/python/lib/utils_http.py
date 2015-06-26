#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python motu client v.1.0.8
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

import urllib
import urllib2
import httplib
import cookielib
import utils_log
import logging
import ssl
import socket

class TLS1Connection(httplib.HTTPSConnection):
    """Like HTTPSConnection but more specific"""
    def __init__(self, host, **kwargs):
        httplib.HTTPSConnection.__init__(self, host, **kwargs)
 
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
                ssl_version=ssl.PROTOCOL_TLSv1)
 
class TLS1Handler(urllib2.HTTPSHandler):
    """Like HTTPSHandler but more specific"""
    def __init__(self):
        urllib2.HTTPSHandler.__init__(self)
 
    def https_open(self, req):
        return self.do_open(TLS1Connection, req)

# Overide default handler
urllib2.install_opener(urllib2.build_opener(TLS1Handler()))

class HTTPErrorProcessor(urllib2.HTTPErrorProcessor):
    def https_response(self, request, response):
        # Consider error codes that are not 2xx (201 is an acceptable response)
        code, msg, hdrs = response.code, response.msg, response.info()
        if code >= 300: 
            response = self.parent.error('http', request, response, code, msg, hdrs)
        return response


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
    # common handlers
    handlers = [urllib2.HTTPCookieProcessor(cookielib.CookieJar()),
                urllib2.HTTPHandler(),
                TLS1Handler(),
                utils_log.HTTPDebugProcessor(log),
                HTTPErrorProcessor()                    
               ]

    # print "AAAAAAAAAAAA kargsParam"               
    # for key, value in kargsParam.items():
        # print key, value                
               
    kargs = kargsParam.copy();
    
    # print "BBBBBBBBBBB kargs"               
    # for key, value in kargs.items():
        # print key, value                

    # add handlers for managing proxy credentials if necessary        
    if kargs.has_key('proxy'):
        urlProxy = ''
        if kargs['proxy'].has_key('user'):
            urlProxy = kargs['proxy']['user'] + ':' + kargs['proxy']['password'] + '@'

        urlProxy += kargs['proxy']['netloc'] 

        handlers.append( urllib2.ProxyHandler({'http':urlProxy, 'https':urlProxy}) )
        handlers.append( urllib2.HTTPBasicAuthHandler() )
        
        del kargs['proxy']
        
    if kargs.has_key('authentication'):
        # create the password manager
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm(ssl_version=ssl.PROTOCOL_TLSv1)
        urlPart = url.partition('?')
        password_mgr.add_password(None, urlPart, kargs['authentication']['user'], kargs['authentication']['password'])
        # add the basic authentication handler
        handlers.append(urllib2.TLS1Handler(password_mgr))
        del kargs['authentication']
    
    if kargs.has_key('data'):
        data = kargs['data']
        del kargs['data']
    
    _opener = urllib2.build_opener(*handlers)
    log.log( utils_log.TRACE_LEVEL, 'list of handlers:' )
    for h in _opener.handlers:
        log.log( utils_log.TRACE_LEVEL, ' . %s',str(h))

    # create the request
    if( data != None ):
        r = urllib2.Request(url, data, **kargs)
    else:
        r = urllib2.Request(url, **kargs)
  
    # print "CCCCCCC kargs"               
    # for key, value in kargs.items():
        # print key, value                

    # open the url, but let the exception propagates to the caller  
    return _opener.open(r)

def encode(options):    
    opts = []
    for k, vset in options.dict().iteritems():
        for v in vset:
           opts.append('%s=%s' % (str(k), str(v).replace('#','%23').replace(' ','%20')))
    return '&'.join(opts)
