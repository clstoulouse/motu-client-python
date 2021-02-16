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

import logging
import re
import sys
import time


if sys.version_info > (3, 0):
    import urllib.request, urllib.error
    from urllib.parse import parse_qs, urlparse, quote, quote_plus
else:
    from urllib import quote_plus, quote
    from urlparse import urlparse, parse_qs

from motu_utils import utils_http, utils_log, utils_html, utils_messages
from motu_utils import utils_collection


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
    delays = [10, 30, 100, 300]
    nbDelays = len(delays)
    tries = 0
    redirected = False
    while not redirected and tries<=nbDelays:
        try:
            connexion = utils_http.open_url(url, **url_config)
            # connexion response code must be a redirection, else, there's an error (user can't be already connected since no cookie or ticket was sent)
            if connexion.url != url:
                # find the cas url from the redirected url
                redirected_url = connexion.url
                p = parse_qs(urlparse(connexion.url).query, keep_blank_values=False)
                redirectServiceUrl = p['service'][0]
                m = re.search(CAS_URL_PATTERN, redirected_url)
                if not m is None:
                    redirected = True
        except Exception as e:
            if hasattr(e, 'code') and e.code == 400:
                log_error_password(log)
                raise e
            else:
              if not redirected and tries<nbDelays:
                log.warn("Warning: CAS connection failed, retrying in " + str(delays[tries]) + " seconds ...")
                time.sleep(delays[tries])
                tries = tries + 1
              else:
                raise e
        
    if not redirected:
        if redirected_url is None:
            raise Exception(
                utils_messages.get_external_messages()['motuclient.exception.authentication.not-redirected'] % server)
        else:
            raise Exception(
                utils_messages.get_external_messages()['motuclient.exception.authentication.unfound-url'] % redirected_url)
    
    url_cas = m.group(1) + '/v1/tickets'
    opts = utils_http.encode(utils_collection.ListMultimap(username = quote(user), password = quote(pwd) ))

    utils_log.log_url(log, "login user into CAS:\t", url_cas + '?' + opts)
    url_config['data']=opts.encode()
    
    connected = False
    tries = 0
    while not connected and tries<=nbDelays:
        try:
            connexion = utils_http.open_url(url_cas, **url_config)
            connected = True
        except Exception as e:
            if hasattr(e, 'code') and e.code == 400:
                log_error_password(log)
                raise e
            else:
                if tries<nbDelays:
                    log.warn("Warning: Authentication failed, retrying in " + str(delays[tries]) + " seconds ...")
                    time.sleep(delays[tries])
                    tries = tries + 1
                else:
                  raise e
    
    fp = utils_html.FounderParser()
    for line in connexion:
        log.log(utils_log.TRACE_LEVEL, 'utils_html.FounderParser() line: %s', line)
        # py3 compatibility
        if (isinstance(line, bytes)):
            fp.feed(line.decode())
        else:
            fp.feed(line)
        
    tgt = fp.action_[fp.action_.rfind('/') + 1:]
    log.log(utils_log.TRACE_LEVEL, 'TGT: %s', tgt)

    # WARNING : don't use 'fp.action_' as url : it seems protocol is always http never https 
    # use 'url_cas', extract TGT from 'fp.action_' , then construct url_ticket.
    # url_ticket = fp.action_
    url_ticket = url_cas + '/' + tgt

    if url_ticket is None:
        raise Exception(utils_messages.get_external_messages()['motuclient.exception.authentication.tgt'])
    
    utils_log.log_url(log, "found url ticket:\t", url_ticket)

    opts = utils_http.encode(utils_collection.ListMultimap(service = quote_plus(redirectServiceUrl)))

    utils_log.log_url(log, 'Granting user for service\t', url_ticket + '?' + opts)
    url_config['data']=opts.encode()

    validated = False
    tries = 0
    while not validated and tries<=nbDelays:
        try:
            ticket = utils_http.open_url(url_ticket, **url_config).readline()
            validated = True
        except Exception as e:
            if tries<nbDelays:
                log.warn("Warning: Ticket validation failed, retrying in " + str(delays[tries]) + " seconds ...")
                time.sleep(delays[tries])
                tries = tries + 1
            else:
                raise

    # py3 compatibility
    if (isinstance(ticket, bytes)):
        ticket = ticket.decode()

    utils_log.log_url(log, "found service ticket:\t", ticket)
    
    # we append the download url with the ticket and return the result  
    service_url = redirectServiceUrl + '&ticket=' + ticket
    
    utils_log.log_url(log, "service url is:\t", service_url)
      
    return service_url

    
def log_error_password(log):
  log.error( """Error: Bad user login or password:
       [...] -u login -p "password" (or --pwd  "password") [...]    You must use the double quotes for the password.
       If your password containts UTF8 special characters, please refers to https://github.com/clstoulouse/motu-client-python#options
           """)