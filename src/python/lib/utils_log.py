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

import urllib2
import logging

# trace level
TRACE_LEVEL = 1

def log_url(log, message, url, level = logging.DEBUG ):
    """Nicely logs the given url.
    
    Print out the url with the first part (protocol, host, port, authority,
    user info, path, ref) and in sequence all the query parameters.
    
    log: the log into which write the message
    message: a message to print before the url
    url: the url to log
    level: (optional) the log level to use"""
    
    urls = url.split('?')
    log.log( level, message + urllib2.unquote(urls[0]) )
    if len(urls) > 1:
        for a in sorted(urls[1].split('&')):
            param = a.split('=')
            if( len(param) < 2 ):
              param.append('')
            log.log( level, ' . %s = %s', urllib2.unquote(param[0]), urllib2.unquote(param[1]) )

            
class HTTPDebugProcessor(urllib2.BaseHandler):
    """ Track HTTP requests and responses with this custom handler.
    """
    def __init__(self, log, log_level=TRACE_LEVEL):
        self.log_level = log_level
        self.log = log

    def http_request(self, request):
        host, full_url = request.get_host(), request.get_full_url()
        url_path = full_url[full_url.find(host) + len(host):]
        log_url ( self.log, "Requesting: ", request.get_full_url(), TRACE_LEVEL )
        self.log.log(self.log_level, "%s %s" % (request.get_method(), url_path))

        for header in request.header_items():
            self.log.log(self.log_level, " . %s: %s" % header[:])

        return request

    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.headers
        self.log.log(self.log_level, "Response:")
        self.log.log(self.log_level," HTTP/1.x %s %s" % (code, msg))
        
        for headers in hdrs.headers:
            self.log.log(self.log_level, " . %s%s %s" % headers.rstrip().partition(':'))

        return response            
