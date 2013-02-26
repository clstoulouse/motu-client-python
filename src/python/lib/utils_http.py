#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python motu client v.${project.version} 
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

class HTTPErrorProcessor(urllib2.HTTPErrorProcessor):
    def https_response(self, request, response):
        # Consider error codes that are not 2xx (201 is an acceptable response)
        code, msg, hdrs = response.code, response.msg, response.info()
        if code >= 300: 
            response = self.parent.error('http', request, response, code, msg, hdrs)
        return response


def open_url(url, **kargs):
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
                urllib2.HTTPSHandler(),
                utils_log.HTTPDebugProcessor(log),
                HTTPErrorProcessor()                    
               ]

    # add handlers for managing proxy credentials if necessary        
    if kargs.has_key('proxy'):
        # extract protocol            
        #log.log( utils_log.TRACE_LEVEL, ' PROXY. %s',kargs['proxy']['scheme'])
        #log.log( utils_log.TRACE_LEVEL, ' PORT . %s',kargs['proxy']['netloc'])
        #handlers.append( urllib2.ProxyHandler({kargs['proxy']['scheme']:kargs['proxy']['netloc']}) )
        handlers.append( urllib2.ProxyHandler({'http':kargs['proxy']['netloc'], 'https':kargs['proxy']['netloc']}) )
        if kargs['proxy'].has_key('user'):
            proxy_auth_handler = urllib2.HTTPBasicAuthHandler()
            proxy_auth_handler.add_password('realm', kargs['proxy']['user'], 'username', kargs['proxy']['password'])
            handlers.append(proxy_auth_handler)
        del kargs['proxy']
        
    if kargs.has_key('authentication'):
        # create the password manager
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        urlPart = url.partition('?')
        password_mgr.add_password(None, urlPart, kargs['authentication']['user'], kargs['authentication']['password'])
        # add the basic authentication handler
        handlers.append(urllib2.HTTPBasicAuthHandler(password_mgr))
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
  
    # open the url, but let the exception propagates to the caller  
    return _opener.open(r)

def encode(options):    
    opts = []
    for k, vset in options.dict().iteritems():
        for v in vset:
           opts.append('%s=%s' % (str(k), str(v).replace('#','%23').replace(' ','%20')))
    return '&'.join(opts)