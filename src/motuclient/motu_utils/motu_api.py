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

from pkg_resources import get_distribution
from xml.dom import minidom
import platform
import traceback
import socket
import time
import datetime
import re
import os
import sys
import netrc
import logging
import logging.config

# Import project libraries
from motu_utils import utils_collection
from motu_utils import utils_http, utils_stream, utils_cas, utils_messages, utils_unit, \
    stop_watch, utils_log

if sys.version_info > (3, 0):
    from urllib.parse import quote_plus, urlparse
else:
    from urllib import quote_plus
    from urlparse import urlparse


# constant for authentication modes
AUTHENTICATION_MODE_NONE = 'none'
AUTHENTICATION_MODE_BASIC = 'basic'
AUTHENTICATION_MODE_CAS = 'cas'

# constant for date time string format
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


log = None

# Used to display download progress
lastProgressPercentValue = 0.0


def get_client_version():
    """Return the version (as a string) of this client.

    The value is automatically set by the maven processing build, so don't
    touch it unless you know what you are doing."""
    version = 'unknown'
    try:
        version = get_distribution('motuclient').version
    except Exception:
        version = "Undefined"
    return version


def get_client_artefact():
    """Return the artifact identifier (as a string) of this client.

    The value is automatically set by the maven processing build, so don't
    touch it unless you know what you are doing."""
    return 'motuclient-python'


def build_params(_options):
    """Function that builds the query string for Motu according to the given options"""

    """
    Build the main url to connect to
    """
    query_options = utils_collection.ListMultimap()

    # describeProduct in XML format (sync) / productDownload (sync/async)
    if _options.describe:
        query_options.insert(action='describeProduct',
                             service=_options.service_id,
                             product=_options.product_id
                             )
    elif _options.size:
        query_options.insert(action='getSize',
                             service=_options.service_id,
                             product=_options.product_id
                             )
    elif _options.sync:
        log.info('Synchronous mode set')
        query_options.insert(action='productdownload',
                             scriptVersion=quote_plus(
                                 get_client_version()),
                             mode='console',
                             service=_options.service_id,
                             product=_options.product_id
                             )
    else:
        log.info('Asynchronous mode set')
        query_options.insert(action='productdownload',
                             scriptVersion=quote_plus(
                                 get_client_version()),
                             mode='status',
                             service=_options.service_id,
                             product=_options.product_id
                             )

    # geographical parameters
    if _options.extraction_geographic:
        query_options.insert(x_lo=_options.longitude_min,
                             x_hi=_options.longitude_max,
                             y_lo=_options.latitude_min,
                             y_hi=_options.latitude_max
                             )

    if _options.depth_min is not None or _options.depth_max is not None:
        query_options.insert(z_lo=_options.depth_min,
                             z_hi=_options.depth_max
                             )

    """ MOTU-172
    if _options.extraction_output:
        query_options.insert(output=_options.outputWritten)
    else:"""
    query_options.insert(output="netcdf")

    # date are date time. They should be converted to the proper format to Motu
    if _options.date_min is not None:
        date_min = _options.date_min.strftime(DATETIME_FORMAT)
        query_options.insert(t_lo=date_min)

    if _options.date_max is not None:
        date_max = _options.date_max.strftime(DATETIME_FORMAT)
        query_options.insert(t_hi=date_max)

    variable = _options.variable
    if variable is not None:
        for i, opt in enumerate(variable):
            query_options.insert(variable=opt)

    if _options.console_mode or _options.out_dir.startswith("console"):
        query_options.insert(mode="console")

    return utils_http.encode(query_options)


def check_options(_options):
    """function that checks the given options for coherency."""

    # Check Mandatory Options on AUTHENTICATION
    if (_options.auth_mode != AUTHENTICATION_MODE_NONE and 
        _options.auth_mode != AUTHENTICATION_MODE_BASIC and
        _options.auth_mode != AUTHENTICATION_MODE_CAS):
        raise Exception(utils_messages.get_external_messages()['motuclient.exception.option.invalid'] % (_options.auth_mode, 'auth-mode', [AUTHENTICATION_MODE_NONE, AUTHENTICATION_MODE_BASIC, AUTHENTICATION_MODE_CAS]))

    # those following parameters are required
    if _options.motu is None:
        raise Exception(utils_messages.get_external_messages()[
                        'motuclient.exception.option.mandatory'] % 'motu')

    if (_options.auth_mode != AUTHENTICATION_MODE_NONE) and (_options.user is None or _options.pwd is None):
        # if authentication mode is set we check both user & password presence
        try:
            n = netrc.netrc()
            cred = n.authenticators(_options.motu.split('/')[2])
            if cred is not None:
                _options.user = cred[0]
                _options.pwd = cred[2]
        except Exception as ex:
            log.warn("Unable to read netrc configuration: %s" % ex)
        if _options.user is None:
            raise Exception(utils_messages.get_external_messages()['motuclient.exception.option.mandatory.user'] % ('user', _options.auth_mode))
        elif _options.pwd is None:
            raise Exception(utils_messages.get_external_messages()['motuclient.exception.option.mandatory.password'] % ('pwd', _options.user))
    elif (_options.auth_mode == AUTHENTICATION_MODE_NONE and _options.user is not None):
        # check that if a user is set, an authentication mode should also be set
        raise Exception(utils_messages.get_external_messages()['motuclient.exception.option.mandatory.mode'] % (
            AUTHENTICATION_MODE_NONE, 'auth-mode', _options.user))
    elif (_options.pwd is None and _options.user is not None):
        # check that if a user is set, a password should be set also
        raise Exception(utils_messages.get_external_messages()[
                        'motuclient.exception.option.mandatory.password'] % ('pwd', _options.user))

    if _options.service_id is None:
        raise Exception(utils_messages.get_external_messages()[
                        'motuclient.exception.option.mandatory'] % 'service-id')

    if _options.product_id is None:
        raise Exception(utils_messages.get_external_messages()[
                        'motuclient.exception.option.mandatory'] % 'product-id')

    if _options.out_dir is None:
        raise Exception(utils_messages.get_external_messages()[
                        'motuclient.exception.option.mandatory'] % 'out-dir')

    out_dir = _options.out_dir
    if not out_dir.startswith("console"):
        # check directory existence
        if not os.path.exists(out_dir):
            raise Exception(
                utils_messages.get_external_messages()['motuclient.exception.option.outdir-notexist'] % out_dir)
        # check whether directory is writable or not
        if not os.access(out_dir, os.W_OK):
            raise Exception(
                utils_messages.get_external_messages()['motuclient.exception.option.outdir-notwritable'] % out_dir)

        if _options.out_name is None:
            raise Exception(
                utils_messages.get_external_messages()['motuclient.exception.option.mandatory'] % 'out-name')

    # Check PROXY Options
    _options.proxy = False
    if (_options.proxy_server is not None) and (len(_options.proxy_server) != 0):
        _options.proxy = True
        # check that proxy server is a valid url
        url = _options.proxy_server
        p = re.compile(
            '^(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?')
        m = p.match(url)

        if not m:
            raise Exception(utils_messages.get_external_messages()[
                            'motuclient.exception.option.not-url'] % ('proxy-server', url))
        # check that if proxy-user is defined then proxy-pwd shall be also, and reciprocally.
        if (_options.proxy_user is not None) != (_options.proxy_pwd is not None):
            raise Exception(utils_messages.get_external_messages()[
                            'motuclient.exception.option.linked'] % ('proxy-user', 'proxy-name'))

    # Check VERTICAL Options
    # No need

    # Check TEMPORAL  Options
    # No need

    """ MOTU-172
    #Check OUTPUT Options
    _options.extraction_output = False
    if _options.outputWritten is not None :
        _options.extraction_output = True
    """
    # Check GEOGRAPHIC Options
    _options.extraction_geographic = False
    if _options.latitude_min is not None or _options.latitude_max is not None or _options.longitude_min is not None or _options.longitude_max is not None:
        _options.extraction_geographic = True

        check_latitude(_options.latitude_min, 'latitude_min')
        check_latitude(_options.latitude_max, 'latitude_max')

        check_coordinate(_options.longitude_min, 'longitude_min')
        check_coordinate(_options.longitude_max, 'longitude_max')


def check_coordinate(coord, msg):
    if(coord is None):
        raise Exception(
            utils_messages.get_external_messages()['motuclient.exception.option.geographic-box'] % msg)
    try:
        return float(coord)
    except ValueError:
        raise Exception(utils_messages.get_external_messages()[
                        'motuclient.exception.option.invalid'] % (coord, msg, 'floating point number'))


def check_latitude(lat, msg):
    tempvalue = check_coordinate(lat, msg)
    if tempvalue < -90 or tempvalue > 90:
        raise Exception(utils_messages.get_external_messages()[
                        'motuclient.exception.option.out-of-range'] % (msg, str(tempvalue)))


def get_url_config(_options, data=None):
    # prepare arguments
    kargs = {}
    # proxy
    if _options.proxy:
        # proxyUrl = _options.proxy_server.partition(':')
        proxyUrl = urlparse(_options.proxy_server)
        kargs['proxy'] = {"scheme": proxyUrl.scheme,
                          "netloc": proxyUrl.netloc}
        if _options.proxy_user is not None:
            kargs['proxy']['user'] = _options.proxy_user
            kargs['proxy']['password'] = _options.proxy_pwd
    # authentication
    if _options.auth_mode == AUTHENTICATION_MODE_BASIC:
        kargs['authentication'] = {'mode': 'basic',
                                   'user': _options.user,
                                   'password': _options.pwd}
    # headers
    kargs['headers'] = {"X-Client-Id": get_client_artefact(),
                        "X-Client-Version": quote_plus(get_client_version())}
    # data
    if data is not None:
        kargs['data'] = data

    return kargs


def get_requestUrl(dl_url, server, _options, **options):
    """ Get the request url."""
    stopWatch = stop_watch.localThreadStopWatch()
    stopWatch.start('get_request')
    log.info("Requesting file to download (this can take a while)...")

    # Get request id
    m = utils_http.open_url(dl_url, **options)
    responseStr = m.read()
    dom = minidom.parseString(responseStr)
    node = dom.getElementsByTagName('statusModeResponse')[0]
    status = node.getAttribute('status')
    if status == "2":
        msg = node.getAttribute('msg')
        log.error(msg)
        get_req_url = None
    else:
        requestId = node.getAttribute('requestId')
        # Get request url
        get_req_url = server + '?action=getreqstatus&requestid=' + requestId + \
            "&service=" + _options.service_id + "&product=" + _options.product_id

    stopWatch.stop('get_request')

    return get_req_url


def dl_2_file(dl_url, fh, block_size=65535, isADownloadRequest=None, **options):
    """ Download the file with the main url (of Motu) file.

    Motu can return an error message in the response stream without setting an
    appropriate http error code. So, in that case, the content-type response is
    checked, and if it is text/plain, we consider this as an error.

    dl_url: the complete download url of Motu
    fh: file handler to use to write the downstream"""

    stopWatch = stop_watch.localThreadStopWatch()
    start_time = datetime.datetime.now()
    lastProgressPercentValue = 0.0
    log.info("Downloading file (this can take a while)...")

    # download file
    temp = None
    if not fh.startswith("console"):
        temp = open(fh, 'w+b')

    try:
        stopWatch.start('processing')

        m = utils_http.open_url(dl_url, **options)
        try:
            # check the real url (after potential redirection) is not a CAS Url scheme
            match = re.search(utils_cas.CAS_URL_PATTERN, m.url)
            if match is not None:
                service, _, _ = dl_url.partition('?')
                redirection, _, _ = m.url.partition('?')
                raise Exception(
                    utils_messages.get_external_messages()['motuclient.exception.authentication.redirected'] % (service, redirection))

            # check that content type is not text/plain
            headers = m.info()
            if "Content-Type" in headers and len(headers['Content-Type']) > 0 and isADownloadRequest and (headers['Content-Type'].startswith('text') or headers['Content-Type'].find('html') != -1):
                raise Exception(utils_messages.get_external_messages()[
                                'motuclient.exception.motu.error'] % m.read())

            log.info('File type: %s' % headers['Content-Type'])
            # check if a content length (size of the file) has been send
            size = -1
            if "Content-Length" in headers:
                try:
                    # it should be an integer
                    size = int(headers["Content-Length"])
                    log.info('File size: %s (%i B)' %
                             (utils_unit.convert_bytes(size), size))
                except Exception as e:
                    size = -1
                    log.warn('File size is not an integer: %s' %
                             headers["Content-Length"])
                    log.exception(e)
            elif temp is not None:
                log.warn('File size: %s' % 'unknown')

            processing_time = datetime.datetime.now()
            stopWatch.stop('processing')
            stopWatch.start('downloading')

            # performs the download
            log.info('Downloading file %s' % os.path.abspath(fh))

            def progress_function(sizeRead):
                global lastProgressPercentValue
                percent = sizeRead*100./size
                if percent - lastProgressPercentValue > 1 or (lastProgressPercentValue != 100 and percent >= 100):
                    log.info("Progress - %s (%.1f%%)" % (utils_unit.convert_bytes(size).rjust(8), percent))
                    lastProgressPercentValue = percent

            def none_function(sizeRead):
                global lastProgressPercentValue
                percent = 100
                log.info("Progress - %s (%.1f%%)" % (utils_unit.convert_bytes(size).rjust(8), percent))
                lastProgressPercentValue = percent

            if temp is not None:
                read = utils_stream.copy(
                    m, temp, progress_function if size != -1 else none_function, block_size)
            else:
                if isADownloadRequest:
                    # Console mode, only display the NC file URL on stdout
                    read = len(m.url)
                    log.info((m.url))
                else:
                    import io
                    output = io.StringIO()
                    utils_stream.copy(
                        m, output, progress_function if size != -1 else none_function, block_size)
                    read = len(output.getvalue())
                    log.info((output.getvalue()))

            end_time = datetime.datetime.now()
            stopWatch.stop('downloading')

            log.info("Processing  time : %s" % str(processing_time - init_time))
            log.info("Downloading time : %s" % str(end_time - processing_time))
            log.info("Total time       : %s" % str(end_time - init_time))
            log.info("Download rate    : %s/s" % utils_unit.convert_bytes(int(read / (end_time - start_time).total_seconds())))
            log.info("Save into        : %s" % fh)
        except Exception as e:
            log.error("Download failed: %s" % e)
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
            log.debug("Stack trace exception is detailed hereafter:")
            exc_type, exc_value, exc_tb = sys.exc_info()
            x = traceback.format_exception(exc_type, exc_value, exc_tb)
            for stack in x:
                log.debug(' . %s' % stack.replace('\n', ''))
            log.debug('-'*60)
            log.trace('System info is provided hereafter:')
            system, node, release, version, machine, processor = platform.uname()
            log.trace(' . system   : %s' % system)
            log.trace(' . node     : %s' % node)
            log.trace(' . release  : %s' % release)
            log.trace(' . version  : %s' % version)
            log.trace(' . machine  : %s' % machine)
            log.trace(' . processor: %s' % processor)
            log.trace(' . python   : %s' % sys.version.replace("\n", " "))
            log.trace(' . client   : %s' % get_client_version())

        finally:
            m.close()
    finally:
        if temp is not None:
            temp.flush()
            temp.close()

    # raise exception if actual size does not match content-length header
    if temp is not None and size >= 0 and read < size:
        raise Exception(
            utils_messages.get_external_messages()['motuclient.exception.download.too-short'] % (read, size))


def execute_request(_options, timeout=None):
    """
    the main function that submit a request to motu. Available options are:

    * Proxy configuration (with eventually user credentials)
      - proxy_server: 'http://my-proxy.site.com:8080'
      - proxy_user  : 'john'
      - proxy_pwd   :'doe'

    * Autorisation mode: 'cas', 'basic', 'none'
      - auth_mode: 'cas'

    * User credentials for authentication 'cas' or 'basic'
      - user: 'john'
      - pwd:  'doe'

    * Motu service URL
      - motu: 'http://atoll-dev.cls.fr:30080/mis-gateway-servlet/Motu'

    * Dataset identifier to download
      - product_id: 'dataset-duacs-global-nrt-madt-merged-h'

    * Service identifier to use for retrieving dataset
      - service_id: 'http://purl.org/myocean/ontology/service/database#yourduname'

    * Geographic extraction parameters
      - latitude_max :  10.0
      - latitude_min : -10.0
      - longitude_max: -0.333333333369
      - longitude_min:  0.0

    * Vertical extraction parameters
      - depth_max: 1000
      - depth_min: 0

    * Temporal extraction parameters, as a datetime instance or a string (format: '%Y-%m-%d %H:%M:%S')
      - date_max: '2010-04-25 12:05:36' or datetime.datetime(2010, 4, 25, 12, 5, 36)
      - date_min: '2010-04-25' or datetime.datetime(2010, 4, 25)

    * Variable extraction
      - variable: ['variable1','variable2']

    * The file name and the directory of the downloaded dataset
      - out_dir : '.'
      - out_name: 'dataset'

    * The block size used to perform download
      - block_size: 12001

    * The socket timeout configuration
      - socket_timeout: 515

    * The user agent to use when performing http requests
      - user_agent: 'motu-api-client'

    """
    global log
    global init_time
    
    log = logging.getLogger("motu_api")
    log.trace = lambda arg: utils_log.trace(log, arg)

    log.debug("execute request")
    init_time = datetime.datetime.now()
    stopWatch = stop_watch.localThreadStopWatch()
    stopWatch.start()
    try:
        # at first, we check given options are ok
        log.debug("check option")
        check_options(_options)

        # print some trace info about the options set
        log.trace('-'*60)
        for option in dir(_options):
            if not option.startswith('_') and not option.startswith('pwd'):
                log.trace("%s=%s" % (option, getattr(_options, option)))
        log.trace('-'*60)

        # start of url to invoke
        url_service = _options.motu

        # parameters of the invoked service
        url_params = build_params(_options)

        url_config = get_url_config(_options)

        # check if question mark is in the url
        questionMark = '?'
        if url_service.endswith(questionMark):
            questionMark = ''
        url = url_service+questionMark+url_params

        if _options.describe is True or _options.size is True:
            _options.out_name = _options.out_name.replace('.nc', '.xml')

        # set-up the socket timeout if any
        if _options.socket_timeout is not None:
            log.debug("Setting timeout %s" % _options.socket_timeout)
            socket.setdefaulttimeout(_options.socket_timeout)

        if _options.auth_mode == AUTHENTICATION_MODE_CAS:
            stopWatch.start('authentication')
            # perform authentication before acceding service
            download_url = utils_cas.authenticate_CAS_for_URL(url,
                                                              _options.user,
                                                              _options.pwd, timeout=timeout, **url_config)
            url_service = download_url.split("?")[0]
            stopWatch.stop('authentication')
        else:
            # if none, we do nothing more, in basic, we let the url requester doing the job
            download_url = url

        # create a file for storing downloaded stream
        log.trace("create file")
        fh = os.path.join(_options.out_dir, _options.out_name)
        if _options.console_mode:
            fh = "console"

        try:
            # Synchronous mode
            if _options.sync is True or _options.describe is True or _options.size is True:
                log.debug("Synchronous connection")
                is_a_download_request = False
                if _options.describe is False and _options.size is False:
                    is_a_download_request = True
                dl_2_file(download_url, fh, _options.block_size,
                          is_a_download_request, **url_config)
                log.info("Done")
            # Asynchronous mode
            else:
                log.debug("Asynchronous connection")
                stopWatch.start('wait_request')
                requestUrl = get_requestUrl(download_url, url_service, _options, **url_config)

                if requestUrl is not None:
                    # asynchronous mode
                    status = "0"
                    dwurl = ""
                    msg = ""

                    date_start = datetime.datetime.now()
                    while True:
                        if _options.auth_mode == AUTHENTICATION_MODE_CAS:
                            stopWatch.start('authentication')
                            # perform authentication before acceding service
                            requestUrlCas = utils_cas.authenticate_CAS_for_URL(requestUrl,
                                                                               _options.user,
                                                                               _options.pwd, **url_config)
                            stopWatch.stop('authentication')
                        else:
                            # if none, we do nothing more, in basic, we let the url requester doing the job
                            requestUrlCas = requestUrl

                        m = utils_http.open_url(requestUrlCas, **url_config)
                        motu_reply = m.read()
                        dom = None

                        try:
                            dom = minidom.parseString(motu_reply)
                        except Exception:
                            log.error("Motu Error reply %s" % motu_reply)
                            dom = None

                        if dom:
                            for node in dom.getElementsByTagName('statusModeResponse'):
                                status = node.getAttribute('status')
                                dwurl = node.getAttribute('remoteUri')
                                msg = node.getAttribute('msg')
                        else:
                            status = "4"

                        # Check status
                        if status == "0" or status == "3":  # in progress/pending
                            log.info('Product is not yet available (request in progress)')
                            time.sleep(10)
                        else:  # finished (error|success)
                            break

                        if timeout is not None and (datetime.datetime.now() - date_start) > timeout:
                            log.warn("Aborting request under reception global timeout %s" % timeout)
                            try:
                                if (os.path.isfile(fh)):
                                    os.remove(fh)
                            except Exception:
                                pass
                            break

                    if status == "2":
                        log.error(msg)
                    if status == "4":
                        log.error(
                            "Motu server API interaction appears to have failed, server response is invalid")
                    if status == "1":
                        log.info('The product is ready for download')
                        if dwurl != "":
                            dl_2_file(dwurl, fh, _options.block_size, not (
                                _options.describe or _options.size), **url_config)
                            log.info("Done")
                        else:
                            log.error("Couldn't retrieve file")

                stopWatch.stop('wait_request')

        except Exception:
            # Remove the file under exception
            try:
                if (os.path.isfile(fh)):
                    os.remove(fh)
            except Exception:
                pass
            raise
    finally:
        stopWatch.stop()
