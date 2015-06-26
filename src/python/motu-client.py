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
import traceback
import platform
import sys
import httplib
import os
import re
import tempfile
import datetime
import shutil
import zipfile
import logging
import logging.config
import ConfigParser
import optparse
import socket

# The necessary required version of Python interpreter
REQUIRED_VERSION = (2,7)

# error code to use when exiting after exception catch
ERROR_CODE_EXIT=1

# the config file to load from 
CFG_FILE = '~/motu-client/motu-client-python.ini'
LOG_CFG_FILE = './etc/log.ini'

# project libraries path
LIBRARIES_PATH = os.path.join(os.path.dirname(__file__), './lib')

SECTION = 'Main'

# shared logger
log = None

# shared variables to download
_variables = []

# Manage imports of project libraries
if not os.path.exists(LIBRARIES_PATH):
    sys.stderr.write('\nERROR: can not find project libraries path: %s\n\n' % os.path.abspath(LIBRARIES_PATH))
    sys.exit(1) 
sys.path.append(LIBRARIES_PATH)  

# Import project libraries
import utils_log
import utils_messages
import motu_api

def get_client_version():
    """Return the version (as a string) of this client.
    
    The value is automatically set by the maven processing build, so don't 
    touch it unless you know what you are doing."""
    return '1.0.8'

def get_client_artefact():
    """Return the artifact identifier (as a string) of this client.
    
    The value is automatically set by the maven processing build, so don't 
    touch it unless you know what you are doing."""
    return 'motu-client-python'   
                                     
def load_options():
    """load options to handle"""

    _options = None
    
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
                       const = utils_log.TRACE_LEVEL,
                       dest='log_level')
                       
    parser.add_option( '--user', '-u',
                       help = "the user name (string)")

    parser.add_option( '--pwd', '-p',
                       help = "the user password (string)")
                       
    parser.add_option( '--auth-mode',
                       default = motu_api.AUTHENTICATION_MODE_CAS,
                       help = "the authentication mode: '" + motu_api.AUTHENTICATION_MODE_NONE  +
                              "' (for no authentication), '"+ motu_api.AUTHENTICATION_MODE_BASIC +
                              "' (for basic authentication), or '"+motu_api.AUTHENTICATION_MODE_CAS +
                              "' (for Central Authentication Service) [default: %default]")

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
                       help = "The min date with optional hour resolution (string following format YYYY-MM-DD [HH:MM:SS])")

    parser.add_option( '--date-max', '-T',
                       help = "The max date with optional hour resolution (string following format YYYY-MM-DD [HH:MM:SS])",
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
                       type = 'string',    
                       help = "The min depth (float in the interval [0 ; 2e31] or string 'Surface')")

    parser.add_option( '--depth-max', '-Z',
                       type = 'string',    
                       help = "The max depth (float in the interval [0 ; 2e31] or string 'Surface')")

    parser.add_option( '--variable', '-v',
                       help = "The variable (list of strings)",
                       callback=option_callback_variable,
                       dest="variable",
                       type="string",
                       action="callback")
                       
    parser.add_option( '--sync-mode', '-S',
                       help = "Sets the download mode to synchronous (not recommended)",
                       action='store_true',
					   dest='sync')
					   
    parser.add_option( '--describe-product', '-D',
                       help = "It allows to have all updated information on a dataset. Output is in XML format",
                       action='store_true',
					   dest='describe')					   

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
    parser.add_option( '--user-agent',
                       help = "Set the identification string (user-agent) for HTTP requests. By default this value is 'Python-urllib/x.x' (where x.x is the version of the python interpreter)")                       
                  
    # set default values by picking from the configuration file
    default_values = {}
    default_variables = []
    for option in parser.option_list:        
        if (option.dest != None) and conf_parser.has_option(SECTION, option.dest):
            if (option.dest == "variable"):
                default_variables.append(conf_parser.get(SECTION, option.dest))
                default_values[option.dest] = default_variables
            else:    
                default_values[option.dest] = conf_parser.get(SECTION, option.dest)
    
    parser.set_defaults( **default_values )
                      
    return parser.parse_args()
    
def option_callback_variable(option, opt, value, parser):
    global _variables
    _variables.append(value)
    setattr(parser.values, option.dest, _variables)
    
def check_version():
    """Utilitary function that checks the required version of the python interpreter
    is available. Raise an exception if not."""
    
    global REQUIRED_VERSION
    cur_version = sys.version_info
    if (cur_version[0] > REQUIRED_VERSION[0] or
        cur_version[0] == REQUIRED_VERSION[0] and
        cur_version[1] >= REQUIRED_VERSION[1]):   
       return
    else:
       raise Exception( "This tool uses python 2.7 or greater. You version is %s. " % str(cur_version) )
    
#===============================================================================
# The Main function
#===============================================================================
if __name__ == '__main__':
    check_version()
    start_time = datetime.datetime.now()
    
    # first initialize the logger
    logging.addLevelName(utils_log.TRACE_LEVEL, 'TRACE')
    logging.config.fileConfig(  os.path.join(os.path.dirname(__file__),LOG_CFG_FILE) )
    log = logging.getLogger("motu-client-python")
        
    logging.getLogger().setLevel(logging.INFO)
    
    try:
        # we prepare options we want
        (_options, args) = load_options()    

        if _options.log_level != None:
            logging.getLogger().setLevel(int(_options.log_level))
                   
        motu_api.execute_request(_options)       
    except Exception, e:
        log.error( "Execution failed: %s", e )
        if hasattr(e, 'reason'):
          log.info( ' . reason: %s', e.reason )
        if hasattr(e, 'code'):
          log.info( ' . code  %s: ', e.code )
        if hasattr(e, 'read'):
          log.log( utils_log.TRACE_LEVEL, ' . detail:\n%s', e.read() )
        
        log.debug( '-'*60 )
        log.debug( "Stack trace exception is detailed herafter:" )
        exc_type, exc_value, exc_tb = sys.exc_info()
        x = traceback.format_exception(exc_type, exc_value, exc_tb)
        for stack in x:
            log.debug( ' . %s', stack.replace('\n', '') )
        log.debug( '-'*60 )
        log.log( utils_log.TRACE_LEVEL, 'System info is provided hereafter:' )
        system, node, release, version, machine, processor = platform.uname()
        log.log( utils_log.TRACE_LEVEL, ' . system   : %s', system )
        log.log( utils_log.TRACE_LEVEL, ' . node     : %s', node )
        log.log( utils_log.TRACE_LEVEL, ' . release  : %s', release )
        log.log( utils_log.TRACE_LEVEL, ' . version  : %s', version ) 
        log.log( utils_log.TRACE_LEVEL, ' . machine  : %s', machine )
        log.log( utils_log.TRACE_LEVEL, ' . processor: %s', processor )
        log.log( utils_log.TRACE_LEVEL, ' . python   : %s', sys.version )
        log.log( utils_log.TRACE_LEVEL, ' . client   : %s', get_client_version() )
        log.log( utils_log.TRACE_LEVEL, '-'*60 )

        sys.exit(ERROR_CODE_EXIT)

    finally:
        log.debug( "Elapsed time : %s", str(datetime.datetime.now() - start_time) )

