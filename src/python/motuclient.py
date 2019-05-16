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
from cgi import log
if sys.version_info > (3, 0):
    import urllib
    import configparser as ConfigParser
else:
    import urllib2 as urllib
    import ConfigParser

import traceback
import platform
import sys
import os
import datetime
import logging
import logging.config

import optparse
from motu_utils import utils_configpath

# error code to use when exiting after exception catch
ERROR_CODE_EXIT=1

# the config file to load from
CFG_FILE = '~/motuclient/motuclient-python.ini'
LOG_CFG_FILE = './motu_utils/cfg/log.ini'

SECTION = 'Main'

# shared logger
log = None

# shared variables to download
_variables = []

# project libraries path
LIBRARIES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'motu_utils')
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
    return motu_api.get_client_version()

def get_client_artefact():
    """Return the artifact identifier (as a string) of this client.

    The value is automatically set by the maven processing build, so don't
    touch it unless you know what you are doing."""
    return motu_api.get_client_artefact()

def load_options():
    """load options to handle"""

    _options = None

    # create option parser
    parser = optparse.OptionParser(version=get_client_artefact() + ' v' + get_client_version())

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
                       help = "Get all updated information on a dataset. Output is in XML format",
                       action='store_true',
					   dest='describe')

    parser.add_option( '--size',
                       help = "Get the size of an extraction. Output is in XML format",
                       action='store_true',
                       dest='size')

    parser.add_option( '--out-dir', '-o',
                       help = "The output dir where result (download file) is written (string). If it starts with 'console', behaviour is the same as with --console-mode. ",
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

    parser.add_option( '--outputWritten',
                       help = "Optional parameter used to set the format of the file returned by the download request: netcdf or netcdf4. If not set, netcdf is used.")

    parser.add_option( '--console-mode',
                       help = "Optional parameter used to display result on stdout, either URL path to download extraction file, or the XML content of getSize or describeProduct requests.",
                       action='store_true',
                       dest='console_mode')

    parser.add_option( '--config-file',
                       help = "Path of the optional configuration file [default: %s]" % CFG_FILE,
                       action='append',
                       dest="config_file",
                       type="string")

    # create config parser
    conf_parser = ConfigParser.ConfigParser()

    # read configuration file name from cli arguments or use default
    # cant set default in parser.add_option due to optparse/argparse bug:
    # https://bugs.python.org/issue16399
    config_file = parser.parse_args()[0].config_file
    if config_file is None:
        config_file = [CFG_FILE]
    config_file=[os.path.expanduser(x) for x in config_file]
    conf_parser.read(config_file)

    # set default values by picking from the configuration file
    default_values = {}
    default_variables = []
    for option in parser.option_list:
        if (option.dest != None) and conf_parser.has_option(SECTION, option.dest):
            if option.dest == "variable":
                variablesInCfgFile = conf_parser.get(SECTION, option.dest)
                if (not variablesInCfgFile is None) and variablesInCfgFile.strip():
                    allVariablesArray = variablesInCfgFile.split(",")
                    default_variables = default_variables + allVariablesArray
                    default_values[option.dest] = default_variables
            else:
                default_values[option.dest] = conf_parser.get(SECTION, option.dest)

    parser.set_defaults( **default_values )

    return parser.parse_args()

def option_callback_variable(option, opt, value, parser):
    global _variables
    _variables.append(value)
    setattr(parser.values, option.dest, _variables)


def initLogger():
    logging.addLevelName(utils_log.TRACE_LEVEL, 'TRACE')
    logging.config.fileConfig(  os.path.join(os.path.dirname(__file__),LOG_CFG_FILE) )
    global log
    log = logging.getLogger(__name__)

    logging.getLogger().setLevel(logging.INFO)
#===============================================================================
# The Main function
#===============================================================================
def main():
    start_time = datetime.datetime.now()

    initLogger()

    try:
        # we prepare options we want
        (_options, args) = load_options()

        if _options.log_level != None:
            logging.getLogger().setLevel(int(_options.log_level))

        motu_api.execute_request(_options)
    except Exception as e:
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

if __name__ == '__main__':
    main()
