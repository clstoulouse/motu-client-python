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
import traceback
import platform
import sys
import httplib
import HTMLParser
import os
import re
import tempfile
import datetime
import shutil
import zipfile
import cookielib
import logging
import logging.config
import ConfigParser
import optparse
import socket

# The necessary required version of Python interpreter
REQUIRED_VERSION = (2,5)

# the config file to load from 
CFG_FILE = '~/motu-client/motu-client-python.ini'
MESSAGES_FILE = './etc/messages.properties'
LOG_CFG_FILE = './etc/log.ini'

SECTION = 'Main'

TRACE_LEVEL = 1

_GEOGRAPHIC = False
_VERTICAL   = False
_TEMPORAL   = False
_PROXY      = False

_opener = None
_messages = None
_options = None

log = None

#===============================================================================
# Version
#===============================================================================

def get_client_version():
    return '${project.version}'

def get_client_artefact():
    return '${project.artifactId}'    
    
#===============================================================================
# print_url
#===============================================================================
def print_url(message, url, level = logging.DEBUG ):
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
    def __init__(self, log_level=TRACE_LEVEL):
        self.log_level = log_level

    def http_request(self, request):
        host, full_url = request.get_host(), request.get_full_url()
        url_path = full_url[full_url.find(host) + len(host):]
        print_url ( "Requesting: ", request.get_full_url(), TRACE_LEVEL )
        log.log(self.log_level, "%s %s" % (request.get_method(), url_path))

        for header in request.header_items():
            log.log(self.log_level, " . %s: %s" % header[:])

        return request

    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.headers
        log.log(self.log_level, "Response:")
        log.log(self.log_level," HTTP/1.x %s %s" % (code, msg))
        
        for headers in hdrs.headers:
            log.log(self.log_level, " . %s%s %s" % headers.rstrip().partition(':'))

        return response


#===============================================================================
# open_url
#===============================================================================
def open_url(*args, **kargs):
    global _opener, _PROXY, _options
    if _opener is None:    
        # common handlers
        handlers = [urllib2.HTTPCookieProcessor(cookielib.CookieJar()),
                    urllib2.HTTPHandler(),
                    urllib2.HTTPSHandler(),
                    HTTPErrorProcessor(),
                    HTTPDebugProcessor()
                   ]

        # add handlers for managing proxy credentials if necessary        
        if _PROXY:
            # extract protocol
            url = _options.proxy_server.partition(':')
            handlers.append( urllib2.ProxyHandler({url[0]:url[2]}) )
            if (_options.proxy_user != None):
                proxy_auth_handler = urllib2.HTTPBasicAuthHandler()
                proxy_auth_handler.add_password('realm', _options.proxy_user, 'username', _options.proxy_pwd)
                handlers.append(proxy_auth_handler)
        _opener = urllib2.build_opener(*handlers)
        log.log( TRACE_LEVEL, 'list of handlers:' )
        for h in _opener.handlers:
            log.log( TRACE_LEVEL, ' . %s',str(h))

    kargs['headers'] = {"Accept": "text/plain", "X-Client-Id" : "motu-client-python", "X-Client-Version" : "1.0.0"}

    r = urllib2.Request(*args, **kargs)
  
    # open the url, but let the exception propagates to the caller  
    return _opener.open(r)

#===============================================================================
# encode
#===============================================================================
def encode(**kargs):
    opts = []
    for k, v in kargs.iteritems():
        opts.append('%s=%s' % (str(k), str(v)))
    return '&'.join(opts)



#===============================================================================
# HTTPErrorProcessor
#===============================================================================
class HTTPErrorProcessor(urllib2.HTTPErrorProcessor):
    def https_response(self, request, response):
        # Consider error codes that are not 2xx (201 is an acceptable response)
        code, msg, hdrs = response.code, response.msg, response.info()
        if code >= 300: 
            response = self.parent.error('http', request, response, code, msg, hdrs)
        return response

#===============================================================================
# FounderParser
#===============================================================================
class FounderParser(HTMLParser.HTMLParser):
    """
    Parser witch found the form/action section an return it
    """
    def __init__(self, *args, **kargs):
        HTMLParser.HTMLParser.__init__(self, *args, **kargs)
        self.action_ = None

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'form' and 'action' in d:
            self.action_ = d['action']
           
#===============================================================================
# load_options
#===============================================================================
def load_options():
    '''
    load options to handle
    '''
    global _options, TRACE_LEVEL
    
    # create option parser
    parser = optparse.OptionParser(version=get_client_artefact() + ' v' + get_client_version())
    
    # create config parser
    conf_parser = ConfigParser.SafeConfigParser()
    conf_parser.read(os.path.expanduser(CFG_FILE))
                     
    # add available options
    parser.add_option( '--quiet', '-q',
                       help = "prevent any output in stdout",
                       action = 'store_const',
                       const = logging.WARN,
                       dest='log_level')

    parser.add_option( '--verbose',
                       help = "print information in stdout",
                       action='store_const',
                       const = logging.DEBUG,
                       dest='log_level')
 
    parser.add_option( '--noisy',
                       help = "print more information (traces) in stdout",
                       action='store_const',
                       const = TRACE_LEVEL,
                       dest='log_level')
                       
    parser.add_option( '--user', '-u',
                       help = "the user name (string)")

    parser.add_option( '--pwd', '-p',
                       help = "the user password (string)")

    parser.add_option( '--proxy-server',
                       help = "the proxy server (url)")

    parser.add_option( '--proxy-user',
                       help = "the proxy user (string)")

    parser.add_option( '--proxy-pwd',
                       help = "the proxy password (string)")
                       
    parser.add_option( '--motu', '-m',
                       help = "the motu server to use (url)")

    parser.add_option( '--service-id', '-s',
                       help = "The service identifier (string)")
                              
    parser.add_option( '--product-id', '-d',
                       help = "The product (data set) to download (string)")

    parser.add_option( '--date-min', '-t',
                       help = "The min date (string following format YYYY-MM-DD)")

    parser.add_option( '--date-max', '-T',
                       help = "The max date (string following format YYYY-MM-DD)",
                       default = datetime.date.today().isoformat())
               
    parser.add_option( '--latitude-min', '-y',
                       type = 'float',
                       help = "The min latitude (float in the interval [-90 ; 90])")

    parser.add_option( '--latitude-max', '-Y',
                       type = 'float',
                       help = "The max latitude (float in the interval [-90 ; 90])")
               
    parser.add_option( '--longitude-min', '-x',
                       type = 'float',    
                       help = "The min longitude (float in the interval [-180 ; 180])")

    parser.add_option( '--longitude-max', '-X',
                       type = 'float',    
                       help = "The max longitude (float in the interval [-180 ; 180])")
               
    parser.add_option( '--depth-min', '-z',
                       type = 'float',    
                       help = "The min depth (float in the interval [0 ; 2e31])")

    parser.add_option( '--depth-max', '-Z',
                       type = 'float',    
                       help = "The max depth (float in the interval [0 ; 2e31])")

    parser.add_option( '--variable', '-v',
                       help = "The variable (list of strings)",
                       action="append")
                       
    parser.add_option( '--out-dir', '-o',
                       help = "The output dir (string)",
                       default=".")
               
    parser.add_option( '--out-name', '-f',
                       help = "The output file name (string)",
                       default="data.nc")

    parser.add_option( '--block-size',
                       type = 'int',
                       help = "The block used to download file (integer expressing bytes)",
                       default="65536")
                                              
    parser.add_option( '--socket-timeout',
                       type = 'float',
                       help = "Set a timeout on blocking socket operations (float expressing seconds)")                                          
                  
    # set default values by picking from the configuration file
    default_values = {}
    for option in parser.option_list:        
        if (option.dest != None) and conf_parser.has_option(SECTION, option.dest):
            default_values[option.dest] = conf_parser.get(SECTION, option.dest)
    
    parser.set_defaults( **default_values )
                      
    (_options, args) = parser.parse_args()

#===============================================================================
# format_date
#===============================================================================
def format_date(date):
    """
    Format JulianDay date in unix time
    """
    return date.isoformat()


#===============================================================================
# get_product
#===============================================================================
def get_product():
    """
    Return the product string
    """
    global _options
    
    # '#' is a special character in url, so we have to encode it
    return _options.product_id.replace('#', '%23' )
    
    
#===============================================================================
# get_product
#===============================================================================
def get_service():
    """
    Return the service string
    """
    global _options
    
    # '#' is a special character in url, so we have to encode it
    return _options.service_id.replace('#', '%23' )


#===============================================================================
# build_url
#===============================================================================
def build_url():
    global _GEOGRAPHIC, _VERTICAL, _TEMPORAL, _options
    temporal = ''
    geographic = ''
    vertical = ''
    other_opt = ''
    

    """
    Build the main url to connect too
    """
    opts = encode(action = 'productdownload',
                   mode = 'console',
                   service = get_service(),
                   product = get_product(),
                   )
    

    if _GEOGRAPHIC:
        geographic = '&' + encode(
                x_lo = _options.longitude_min,
                x_hi = _options.longitude_max,
                y_lo = _options.latitude_min,
                y_hi = _options.latitude_max,
                )
    
    if _VERTICAL:
        vertical = '&' + encode(z_lo = _options.depth_min,
                z_hi = _options.depth_max,
                )
    
    if _TEMPORAL:
        # we change date types
        date_max = _options.date_max
        if isinstance(date_max, basestring):
            date_max = datetime.date(*(int(x) for x in date_max.split('-')))
        
        date_min = _options.date_min
        if date_min is None or date_min == None:
            date_min = date_max - datetime.timedelta(20)
        elif isinstance(date_min, basestring):
            date_min = datetime.date(*(int(x) for x in date_min.split('-')))
        
        temporal = '&' + encode(t_lo = format_date(date_min),
                t_hi = format_date(date_max),
                )

    variable = _options.variable
    if variable is not None:
        for i, opt in enumerate(variable):
            other_opt = other_opt + '&variable='+opt
    
    return opts + temporal + geographic + vertical + other_opt

#===============================================================================
# check_options
#===============================================================================
def check_options():
    global _GEOGRAPHIC, _VERTICAL, _TEMPORAL, _PROXY, _options
    """
    Check Mandatory Options
    """        
    if _options.user == None :
        raise Exception(getExternalMessages()['motu-client.exception.option.mandatory'] % 'user')

    if _options.pwd == None :
        raise Exception(getExternalMessages()['motu-client.exception.option.mandatory'] % 'pwd')
    
    if _options.motu == None :
        raise Exception(getExternalMessages()['motu-client.exception.option.mandatory'] % 'motu')
    
    if _options.service_id == None :
        raise Exception(getExternalMessages()['motu-client.exception.option.mandatory'] % 'service-id')
    
    if _options.product_id == None :
        raise Exception(getExternalMessages()['motu-client.exception.option.mandatory'] % 'product-id')
    
    if _options.out_dir == None :
        raise Exception(getExternalMessages()['motu-client.exception.option.mandatory'] % 'out-dir')
    
    out_dir = _options.out_dir
    
    # check directory existance
    if not os.path.exists(out_dir):
        raise Exception(getExternalMessages()['motu-client.exception.option.outdir-notexist'] % out_dir)
    # check whether directory is writable or not
    if not os.access(out_dir, os.W_OK):
        raise Exception(getExternalMessages()['motu-client.exception.option.outdir-notwritable'] % out_dir)
    
    if _options.out_name == None :
        raise Exception(getExternalMessages()['motu-client.exception.option.mandatory'] % 'out-name')

    """
    Check PROXY Options
    """
    if _options.proxy_server != None:
        _PROXY = True
        # check that proxy server is a valid url
        url = _options.proxy_server
        p = re.compile('^(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?')
        m = p.match(url)
        if not m :
            raise Exception( getExternalMessages()['motu-client.exception.not-url'] % ( 'proxy-server', url ) )
        # check that if proxy-user is defined then proxy-pwd shall be also, and reciprocally.
        if (_options.proxy_user != None) != ( _options.proxy_pwd != None ) :
            raise Exception( getExternalMessages()['motu-client.exception.option.linked'] % ('proxy-user', 'proxy-name') )
    
        
    """
    Check VERTICAL Options
    """
    if _options.depth_min != None and _options.depth_max != None :
        _VERTICAL = True
        tempvalue = float(_options.depth_min)
        if tempvalue < 0 :
            raise Exception( getExternalMessages()['motu-client.exception.option.out-of-range'] % ( 'depth_min', str(tempvalue)) ) 
        tempvalue = float(_options.depth_max)
        if tempvalue < 0 :
            raise Exception( getExternalMessages()['motu-client.exception.option.out-of-range'] % ( 'depth_max', str(tempvalue)) ) 
        
    
    """
    Check TEMPORAL  Options
    """
    if _options.date_min != None and _options.date_max != None :
        _TEMPORAL = True
    
    
    """
    Check GEOGRAPHIC Options
    """
    if _options.latitude_min != None or _options.latitude_max != None or _options.longitude_min != None or _options.longitude_max != None :
        _GEOGRAPHIC = True
        if( _options.latitude_min == None ):
            raise Exception(getExternalMessages()['motu-client.exception.option.geographic-box'] % 'latitude_min' )

        if( _options.latitude_max == None ):
            raise Exception(getExternalMessages()['motu-client.exception.option.geographic-box'] % 'latitude_max' )            
        
        if( _options.longitude_min == None ):
            raise Exception(getExternalMessages()['motu-client.exception.option.geographic-box'] % 'longitude_min' )
        
        if( _options.longitude_max == None ):
            raise Exception(getExternalMessages()['motu-client.exception.option.geographic-box'] % 'longitude_max' )
        
        tempvalue = float(_options.latitude_min)
        if tempvalue < -90 or tempvalue > 90 :
            raise Exception( getExternalMessages()['motu-client.exception.option.out-of-range'] % ( 'latitude_min', str(tempvalue)) )
        tempvalue = float(_options.latitude_max)
        if tempvalue < -90 or tempvalue > 90 :
            raise Exception(getExternalMessages()['motu-client.exception.option.out-of-range'] % ( 'latitude_max', str(tempvalue)))
        tempvalue = float(_options.longitude_min)
        if tempvalue < -180 or tempvalue > 180 :
            raise Exception(getExternalMessages()['motu-client.exception.option.out-of-range'] % ( 'logitude_min', str(tempvalue)))
        tempvalue = float(_options.longitude_max)
        if tempvalue < -180 or tempvalue > 180 :
            raise Exception(getExternalMessages()['motu-client.exception.option.out-of-range'] % ( 'longitude_max', str(tempvalue)))                    
    
#===============================================================================
# get_ticket
#===============================================================================
def get_ticket(url, main_url, usr, pwd):
    """
    Return the ticket for the download
    """
    url = urllib.unquote(url)

    m = re.search('(https://.+/cas)', url)
    if m is None:
        raise Exception(getExternalMessages()['motu-client.exception.authentication.unfound-url'] % url)
    url_cas = m.group(1) + '/v1/tickets'

    log.debug( "url cas:\t%s" %  url_cas )

    opts = encode(username = usr,
                  password = pwd)
    connexion = open_url(url_cas, opts)

    fp = FounderParser()
    for line in connexion:
        fp.feed(line)

    url_ticket = fp.action_
    if url_ticket is None:
        raise Exception(getExternalMessages()['motu-client.exception.authentication.tgt'])

    print_url( "url ticket:\t",url_ticket)
    print_url( "url service\t", url)
    print_url( "main url:\t", main_url)

    opts = encode(service = main_url)
    return open_url(url_ticket, opts).readline()


#===============================================================================
# dl_2_file
#===============================================================================
def dl_2_file(url, ticket, fh):
    """
    Download the file with the main url (of Motu), the ticket and the destination
    file.
    Motu can return an error message in the response stream without setting an
    appropriate http error code. So, in that case, the content-type response is
    checked, and if it is text/plain, we consider this as an error.    
    """
    
    log.info( "Requesting file to download..." )
    
    dl_url = url + '&ticket=' + ticket
    
    
    temp = open(fh, 'w+b')             
    try:
      m = open_url(dl_url)
      try:
        # check that content type is not text/plain
        headers = m.info()
        if "Content-Type" in headers:
          if len(headers['Content-Type']) > 0:
            if   headers['Content-Type'].startswith('text') or headers['Content-Type'].find('html') != -1:
               raise Exception( getExternalMessages()['motu-client.exception.motu.error'] % m.read() )
          
          log.info( 'File type: %s' % headers['Content-Type'] )
        
        if "Content-Length" in headers:
          log.info( 'File size: %s bytes' % headers['Content-Length'] )
          size = int(headers["Content-Length"])     
        else:
          size = -1
          log.warn( 'File size: %s' % 'unknown' )
        
        log.info( 'Downloading file %s:' % os.path.abspath(fh) )

        padding = len(str(size)) 
        read = 0        
        while 1:
           block = m.read(_options.block_size)
           if block == "":
               break;
           read += len(block)
           temp.write(block)
           if True:
               percent = read*100./size
               log.info( "%s/%i (%.1f%%)", str(read ).rjust(padding), size, percent )
           
      finally:
        m.close()
    finally:
      temp.flush()
      temp.close()

    # raise exception if actual size does not match content-length header
    if size >= 0 and read < size:
        raise ContentTooShortError( getExternalMessages()['motu-client.exception.download.too-short'] % (read, size), result)

#===============================================================================
# main
#===============================================================================
loaded = False
def main():
    """
    the main function
    """
    global loaded, log, _options
       
    # first initialize the logger
    logging.addLevelName(TRACE_LEVEL, 'TRACE')
    logging.config.fileConfig(  os.path.join(os.path.dirname(__file__),LOG_CFG_FILE) )
    log = logging.getLogger("motu-client-python")

    log.setLevel(logging.INFO)
    
    if not loaded:
        # we prepare options we want
        load_options()
        loaded = True

    if _options.log_level != None:
        log.setLevel( _options.log_level )
       
    # then we check given options are ok
    check_options()

    # print some trace info about the options set
    log.log( TRACE_LEVEL, '-'*60 )
    log.log( TRACE_LEVEL, '[%s]' % SECTION )
    
    for option in dir(_options):
        if not option.startswith('_'):
            log.log(TRACE_LEVEL, "%s=%s" % (option, getattr( _options, option ) ) )

    log.log( TRACE_LEVEL, '-'*60 )
    
    
    # we build the url
    main_cas_url = _options.motu + urllib.quote_plus(build_url())

    main_url = _options.motu + build_url()
           
    # now we connect
    # if a problem append, an exception is thrown
    log.info("Contacting server")

    # set-up the socket timeout if any
    if _options.socket_timeout != None:
        socket.setdefaulttimeout(_options.socket_timeout)
    
    connexion = open_url(main_url)

    log.info( 'Authenticating user %s' % _options.user )
    ticket = get_ticket(connexion.url,
                        main_cas_url,
                        _options.user,
                        _options.pwd)
    log.debug( 'ticket: %s' % ticket )
    
    fh = os.path.join(_options.out_dir,_options.out_name)
    dl_2_file(main_url, ticket, fh)

#===============================================================================
# external messages
#===============================================================================
def getExternalMessages():
    global _messages
    if _messages is None:
        propFile= file( os.path.join(os.path.dirname(__file__),MESSAGES_FILE), "rU" )
        propDict= dict()
        for propLine in propFile:
            propDef= propLine.strip()
            if len(propDef) == 0:
                continue
            if propDef[0] in ( '!', '#' ):
                continue
            punctuation= [ propDef.find(c) for c in ':= ' ] + [ len(propDef) ]
            found= min( [ pos for pos in punctuation if pos != -1 ] )
            name= propDef[:found].rstrip()
            value= propDef[found:].lstrip(":= ").rstrip()
            propDict[name]= value
        propFile.close()
        _messages = propDict
    return _messages

    
def check_version():
    global REQUIRED_VERSION
    cur_version = sys.version_info
    if (cur_version[0] > REQUIRED_VERSION[0] or
        cur_version[0] == REQUIRED_VERSION[0] and
        cur_version[1] >= REQUIRED_VERSION[1]):   
       return
    else:
       raise Exception( "This tool uses python 2.5 or greater. You version is %s. " % str(cur_version) )
    
#===============================================================================
# The Main function
#===============================================================================
if __name__ == '__main__':
    check_version()
    start_time = datetime.datetime.now()
    try:                
        main()
    except Exception, e:
        log.error( "Execution failed: %s", e )
        if hasattr(e, 'reason'):
          log.info( ' . reason: %s', e.reason )
        if hasattr(e, 'code'):
          log.info( ' . code  %s: ', e.code )
        if hasattr(e, 'read'):
          log.info( ' . detail:\n%s', e.read() )
        
        log.debug( '-'*60 )
        log.debug( "Stack trace exception is detailed herafter:" )
        exc_type, exc_value, exc_tb = sys.exc_info()
        x = traceback.format_exception(exc_type, exc_value, exc_tb)
        for stack in x:
            log.debug( ' . %s', stack.replace('\n', '') )
        log.debug( '-'*60 )
        log.log( TRACE_LEVEL, 'System info is provided hereafter:' )
        system, node, release, version, machine, processor = platform.uname()
        log.log( TRACE_LEVEL, ' . system   : %s', system )
        log.log( TRACE_LEVEL, ' . node     : %s', node )
        log.log( TRACE_LEVEL, ' . release  : %s', release )
        log.log( TRACE_LEVEL, ' . version  : %s', version ) 
        log.log( TRACE_LEVEL, ' . machine  : %s', machine )
        log.log( TRACE_LEVEL, ' . processor: %s', processor )
        log.log( TRACE_LEVEL, ' . python   : %s', sys.version )
        log.log( TRACE_LEVEL, ' . client   : %s', get_client_version() )
        log.log( TRACE_LEVEL, '-'*60 )
    finally:
        log.debug( "Elapsed time : %s", str(datetime.datetime.now() - start_time) )

