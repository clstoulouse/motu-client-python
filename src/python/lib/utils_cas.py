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

import logging
import re
import urllib
import datetime

import utils_http
import utils_messages
import utils_html
import utils_log
import utils_collection

# pattern used to search for a CAS url within a response
CAS_URL_PATTERN = '(.*)/login.*'

def authenticate_CAS_for_URL(url, user, pwd, **url_config):
    """Performs a CAS authentication for the given URL service and returns
    the service url with the obtained credential.
    
    The following algorithm is done:
    1) A connection is opened on the given URL
    2) We check that the response is an HTTP redirection
    3) Redirected URL contains the CAS address
    4) We ask for a ticket for the given user and password
    5) We ask for a service ticket for the given service
    6) Then we return a new url with the ticket attached
    
    url: the url of the service to invoke
    user: the username
    pwd: the password"""
    
    log = logging.getLogger("utils_cas:authenticate_CAS_for_URL")
    
    server, sep, options = url.partition( '?' )
    
    log.info( 'Authenticating user %s for service %s' % (user,server) )      
    
    connexion = utils_http.open_url(url,**url_config)

    # connexion response code must be a redirection, else, there's an error (user can't be already connected since no cookie or ticket was sent)
    if connexion.url == url:
        raise Exception(utils_messages.get_external_messages()['motu-client.exception.authentication.not-redirected'] % server )
    
    # find the cas url from the redirected url
    redirected_url = connexion.url
    
    m = re.search(CAS_URL_PATTERN, redirected_url)
    
    if m is None:
        raise Exception(utils_messages.get_external_messages()['motu-client.exception.authentication.unfound-url'] % redirected_url)
    
    url_cas = m.group(1) + '/v1/tickets'

    opts = utils_http.encode(utils_collection.ListMultimap(username = user, password = pwd))

    utils_log.log_url( log, "login user into CAS:\t", url_cas+'?'+opts )
    url_config['data']=opts
    connexion = utils_http.open_url(url_cas, **url_config)

    fp = utils_html.FounderParser()
    for line in connexion:
        log.log( utils_log.TRACE_LEVEL, 'utils_html.FounderParser() line: %s', line )
        fp.feed(line)
        
    tgt = fp.action_[fp.action_.rfind('/') + 1:]
    log.log( utils_log.TRACE_LEVEL, 'TGT: %s', tgt )

    # WARNING : don't use 'fp.action_' as url : it seems protocol is always http never https 
    # use 'url_cas', extract TGT from 'fp.action_' , then construct url_ticket.
    # url_ticket = fp.action_
    url_ticket = url_cas + '/' + tgt

    if url_ticket is None:
        raise Exception(utils_messages.get_external_messages()['motu-client.exception.authentication.tgt'])
    
    utils_log.log_url( log, "found url ticket:\t",url_ticket)

    opts = utils_http.encode(utils_collection.ListMultimap(service = urllib.quote_plus(url)))
    
    utils_log.log_url( log, 'Granting user for service\t', url_ticket +'?'+opts )    
    url_config['data']=opts
    ticket = utils_http.open_url(url_ticket, **url_config).readline() 
    
    utils_log.log_url( log, "found service ticket:\t", ticket)
    
    # we append the download url with the ticket and return the result
    service_url = url + '&ticket=' + ticket
    
    utils_log.log_url( log, "service url is:\t",service_url)
      
    return service_url

    
