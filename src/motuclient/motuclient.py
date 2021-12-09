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


import argparse
from dateutil.parser import parse as dparse
import datetime
import os
import platform
import sys
import traceback

# Import project libraries
from motu_utils import motu_api
from motu_utils import utils_log, utils_configpath
import logging
import logging.config

if sys.version_info > (3, 0):
    import configparser as ConfigParser
else:
    import ConfigParser


# error code to use when exiting after exception catch
ERROR_CODE_EXIT = 1

# the config file to load from
CFG_FILE = '~/motuclient/motuclient-python.ini'
LOG_CFG_FILE = 'log.ini'

SECTION = 'Main'

# shared logger
log = None
# shared variables to download
_variables = []

def load_options():
    """load options to handle"""

    # create option parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version',
                        version=motu_api.get_client_artefact() + ' v' + motu_api.get_client_version())

    parserCredentials = parser.add_argument_group(title='Credentials',
                                                  description='Options related to user authentication.')

    parserConnect = parser.add_argument_group(title='Connection',
                                              description='Options related to connection to the server.')

    parserProxy = parser.add_argument_group(title='Proxy',
                                            description='Options related to proxy configuration.')

    parserQuery = parser.add_argument_group(title='Query',
                                            description='Options related to query parameters.')

    parserOutput = parser.add_argument_group(title='Output',
                                             description='Options related to log and result output.')

    # add available options
    parserOutput.add_argument( '--quiet', '-q',
                       help = "prevent any output in stdout",
                       action = 'store_const',
                       const = logging.WARNING,
                       dest='log_level')

    parserOutput.add_argument( '--verbose',
                       help = "print information in stdout",
                       action='store_const',
                       const = logging.DEBUG,
                       dest='log_level')

    parserOutput.add_argument( '--noisy',
                       help = "print more information (traces) in stdout",
                       action='store_const',
                       const = utils_log.TRACE_LEVEL,
                       dest='log_level')

    parserCredentials.add_argument('--user', '-u',
                                   help="the user name (string). Can be provided alternatively with netrc file.")

    parserCredentials.add_argument('--pwd', '-p',
                                   help="the user password (string). Can be provided alternatively with netrc file.")

    parserCredentials.add_argument('--auth-mode',
                                   choices=[motu_api.AUTHENTICATION_MODE_NONE, motu_api.AUTHENTICATION_MODE_BASIC, motu_api.AUTHENTICATION_MODE_CAS],
                                   default=motu_api.AUTHENTICATION_MODE_CAS,
                                   help="the authentication mode: '" + motu_api.AUTHENTICATION_MODE_NONE +
                                   "' (for no authentication), '" + motu_api.AUTHENTICATION_MODE_BASIC +
                                   "' (for basic authentication), or '"+motu_api.AUTHENTICATION_MODE_CAS +
                                   "' (for Central Authentication Service) [default: " + motu_api.AUTHENTICATION_MODE_CAS + "]")

    parserProxy.add_argument('--proxy-server',
                             help="the proxy server (url)")

    parserProxy.add_argument('--proxy-user',
                             help="the proxy user (string)")

    parserProxy.add_argument('--proxy-pwd',
                             help="the proxy password (string)")

    parserConnect.add_argument('--motu', '-m',
                               help="the motu server to use (url)")

    parserQuery.add_argument('--service-id', '-s',
                             help="The service identifier (string)")

    parserQuery.add_argument('--product-id', '-d',
                             help="The product (data set) to download (string)")

    parserQuery.add_argument('--date-min', '-t',
                             type=dparse,
                             help="The min date with optional hour resolution (string following format YYYY-MM-DD [HH:MM:SS])")

    parserQuery.add_argument('--date-max', '-T',
                             type=dparse,
                             help="The max date with optional hour resolution (string following format YYYY-MM-DD [HH:MM:SS])",
                             default=datetime.date.today())

    parserQuery.add_argument('--latitude-min', '-y', default=-90.,
                             type=float,
                             help="The min latitude (float in the interval [-90 ; 90]). By default at %(default)s")

    parserQuery.add_argument('--latitude-max', '-Y', default=90.,
                             type=float,
                             help="The max latitude (float in the interval [-90 ; 90]). By default at %(default)s")

    parserQuery.add_argument('--longitude-min', '-x', default=-180.,
                             type=float,
                             help="The min longitude (float). By default at %(default)s")

    parserQuery.add_argument('--longitude-max', '-X', default=180.,
                             type=float,
                             help="The max longitude (float). By default at %(default)s")

    parserQuery.add_argument('--depth-min', '-z',
                             type=str,
                             help="The min depth (float in the interval [0 ; 2e31] or string 'Surface')")

    parserQuery.add_argument('--depth-max', '-Z',
                             type=str,
                             help="The max depth (float in the interval [0 ; 2e31] or string 'Surface')")

    parserQuery.add_argument('--variable', '-v',
                             help="The variable (list of strings)",
                             dest="variable",
                             action='append',
                             nargs='+',
                             type=str)

    parserConnect.add_argument('--sync-mode', '-S',
                               help="Sets the download mode to synchronous (not recommended)",
                               action='store_true',
                               dest='sync')

    parserOutput.add_argument('--describe-product', '-D',
                              help="Get all updated information on a dataset. Output is in XML format",
                              action='store_true',
                              dest='describe')

    parserOutput.add_argument('--size',
                              help="Get the size of an extraction. Output is in XML format",
                              action='store_true',
                              dest='size')

    parserOutput.add_argument('--out-dir', '-o',
                              help="The output dir where result (download file) is written (string). If it starts with 'console', behaviour is the same as with --console-mode.",
                              default=".")

    parserOutput.add_argument('--out-name', '-f',
                              help="The output file name (string)",
                              default="data.nc")

    parserConnect.add_argument('--block-size',
                               type=int,
                               help="The block used to download file (integer expressing bytes)",
                               default="65536")

    parserConnect.add_argument('--socket-timeout',
                               type=float,
                               help="Set a timeout on blocking socket operations (float expressing seconds)")
    parserConnect.add_argument('--user-agent',
                               help="Set the identification string (user-agent) for HTTP requests. By default this value is 'Python-urllib/x.x' (where x.x is the version of the python interpreter)")

    parserOutput.add_argument('--outputWritten',
                              choices=['netcdf'],
                              help="Optional parameter used to set the format of the file returned by the download request, only netcdf is supported. If not set, netcdf is used.")

    parserOutput.add_argument('--console-mode',
                              help="Optional parameter used to display result on stdout, either URL path to download extraction file, or the XML content of getSize or describeProduct requests.",
                              action='store_true',
                              dest='console_mode')

    parser.add_argument('--config-file',
                        default=[CFG_FILE],
                        help="Path of the optional configuration file [Default = %s]" % CFG_FILE,
                        action='append',
                        dest="config_file",
                        type=str)

    # create config parser
    conf_parser = ConfigParser.ConfigParser()

    _options = parser.parse_args(parseArgsStringToArray())
    # flatten the variable lists of lists
    if _options.variable is not None:
        _options.variable = [var for varlists in _options.variable for var in varlists]

    # read configuration file name from cli arguments or use default
    # cant set default in parser.add_option due to optparse/argparse bug:
    # https://bugs.python.org/issue16399
    config_file = _options.config_file
    if config_file is None:
        config_file = [CFG_FILE]
    config_file = [os.path.expanduser(x) for x in config_file]
    conf_parser.read(config_file)

    # set default values by picking from the configuration file
    default_values = {}
    default_variables = []

    if (conf_parser.has_section(SECTION)):
        parser_options = conf_parser.options(SECTION)
        for option in conf_parser.options(SECTION):
            if hasattr(_options, option):
                if option == "variable":
                    variablesInCfgFile = conf_parser.get(SECTION, option)
                    if (variablesInCfgFile is not None) and variablesInCfgFile.strip():
                        allVariablesArray = variablesInCfgFile.split(",")
                        default_variables = default_variables + allVariablesArray
                        default_values[option] = default_variables
                else:
                    default_values[option] = conf_parser.get(SECTION, option)
        parser.set_defaults(**default_values)
        return parser.parse_args(parseArgsStringToArray())
    else:
        return _options

def parseArgsStringToArray(argsString=None):
    # Used to collapse correctly all the arguments even when a space is detected
    # e.g. args="-a 'a1' -b 'b2' -c 'c3' -d 'd-d1 -d2 -d3' -e 'e4'"
    # returns array
    # ["-a a1", "-b b2", "-c c3", "-d d-d1 -d2 -d3", "-e e4"]
    if argsString is None:
        argsString = ""
        i=0
        lastOnlyStartingBySimpleQuote=False
        for v in sys.argv:
            if i != 0:
                strV = str(v)
            
                if not strV.startswith("-"):
                    if lastOnlyStartingBySimpleQuote:
                        lastOnlyStartingBySimpleQuote=False
                        if not (strV.endswith("'") or strV.endswith("\\'")):
                            strV = strV + "'"
                    else:
                        if (strV.startswith("'") or strV.startswith("\\'")):
                            if( not (strV.endswith("'") or strV.endswith("\\'")) ):
                                lastOnlyStartingBySimpleQuote=True
                        else:
                            strV = "'" + strV
                            if (not (strV.endswith("'") or strV.endswith("\\'"))):
                                strV = strV + "'"
                if i != 1:
                    argsString = argsString + " " + strV
                else:
                    argsString = strV
            i+=1
  
    allProgramAuthArSpaces = argsString.split(" ")
    allProgramAuthAr = []
    allProgramAuthArIndex=0
    # Backup value, e.g when case is -d 'd-d1 -d2', d-d1 is vback, then -d2 is added
    vbak = None
    for v in allProgramAuthArSpaces:
        if vbak is not None:
            v = vbak + " " + v
   
        if v.startswith("'") or v.startswith("\\'") or v.startswith("\"") or v.startswith("\\\""):
            if v.endswith("'") or v.endswith("\\'") or v.endswith("\"") or v.endswith("\\\""):
                vbak = None
                if allProgramAuthArIndex == 0:
                    allProgramAuthAr.append(v)
                else:
                    oldV = allProgramAuthAr.pop(allProgramAuthArIndex-1)
                    allProgramAuthAr.insert(allProgramAuthArIndex-1, oldV + "=" + v)
            else:
                vbak = v
        else:
            allProgramAuthAr.append(v)
            allProgramAuthArIndex += 1
            vbak = None
    allProgramAuthArRes=[]
    for v in allProgramAuthAr:
        newV = v
        if v.endswith("'"):
            newV = v[:-1]
            if v.startswith("'"):
                newV = v[1:]
            else:
                newV = newV.replace("='", "=", 1)
        allProgramAuthArRes.append(newV)

    return allProgramAuthArRes

  
def initLogger():
    logging.addLevelName(utils_log.TRACE_LEVEL, 'TRACE')
    logging.config.fileConfig(os.path.join(utils_configpath.getConfigPath(), LOG_CFG_FILE))
    global log
    log = logging.getLogger(__name__)
    log.trace = lambda arg: utils_log.trace(log, arg)
    logging.getLogger().setLevel(logging.INFO)

# ===============================================================================
# The Main function
# ===============================================================================


def main():
    start_time = datetime.datetime.now()

    # Configure logger
    initLogger()

    try:
        # we prepare options we want
        _options = load_options()
        if _options.log_level is not None:
            logging.getLogger().setLevel(int(_options.log_level))
        log.debug("start")
        motu_api.execute_request(_options)
    except Exception as e:
        log.exception("Execution failed: %s" % e)
        if hasattr(e, 'reason'):
            log.info(' . reason: %s' % e.reason)
        if hasattr(e, 'code'):
            log.info(' . code  %s: ' % e.code)
        if hasattr(e, 'read'):
            try:
                log.trace(' . detail:\n%s' % e.read())
            except Exception:
                pass
        log.debug('-'*60)
        log.debug("Stack trace exception is detailed hereafter:" )
        exc_type, exc_value, exc_tb = sys.exc_info()
        x = traceback.format_exception(exc_type, exc_value, exc_tb)
        for stack in x:
            log.debug(' . %s', stack.replace('\n', ''))
        log.debug('-'*60)

        log.trace('System info is provided hereafter:')
        system, node, release, version, machine, processor = platform.uname()
        log.trace(' . system   : %s' % system)
        log.trace(' . node     : %s' % node)
        log.trace(' . release  : %s' % release)
        log.trace(' . version  : %s' % version)
        log.trace(' . machine  : %s' % machine)
        log.trace(' . processor: %s' % processor)
        log.trace(' . python   : %s' % sys.version)
        log.trace(' . client   : %s' % motu_api.get_client_version())
        log.trace('-'*60)

        sys.exit(ERROR_CODE_EXIT)

    finally:
        log.debug("Elapsed time : %s" % (datetime.datetime.now() - start_time))


if __name__ == '__main__':
    main()
