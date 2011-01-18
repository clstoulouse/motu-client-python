
========================================================================


                         +--------------------+
                         | Motu python client |
                         +--------------------+


========================================================================

NAME
====

  ./motu-client.py 

The motu python client. You must use python version 2.5 or later.


SYNOPSIS
========

This program can be integrated into a processing chain in order to automate the downloading of products via the Motu.


CONFIGURATION FILE
==================

The program parameters are contained in an ini file. This file is located in the following directory:

   - on Unix platforms: $HOME/motu-client/motu-client-python.ini
   - on Windows platforms: %USERPROFILE%\motu-client/motu-client-python.ini

The expected structure of file is:

  		[Main]
  		user=john
  		pwd=secret
  		log_level=10
  		proxy_server=proxy.domain.net:8080
  		proxy_user=john
  		proxy_pwd=secret
  		motu=http://web-qt.cls.fr/mis-gateway-servlet/Motu?service_id=http//purl.org/myocean/ontology/service/database#CLS-TOULOUSE-FR-MERCATOR-MOTU-REST
  		product_id=dataset-psy2v3-pgs-med-myocean-bestestimate
  		date_min=2010-11-08
  		date_max=2010-11-10
  		latitude_min=-75.0
  		latitude_max=30.0
  		longitude_min=20.0
  		longitude_max=120.0
  		depth_min=
  		depth_max=
  		variable=
  		out_dir=./out_dir
  		out_name=test.nc
  		block_size=65535
  		socket_timeout=


INSTALLATION
============

Deploy the archive in the directory of your choice. Create a configuration file (see "CONFIGURATION FILE") to inform the user and password to use to connect to the CAS server.

Installing Python modules which are not provided in the standard installation of Python. The list of modules to be installed is described in section "REQUIRED MODULES".


USAGE
=====

Usage: ./motu-client.py -h

  	Usage: motu-client.py [options]
  
        Options:
          --version             show program's version number and exit
          -h, --help            show this help message and exit
          -q, --quiet           prevent any output in stdout
          --verbose             print information in stdout
          --noisy               print more information (traces) in stdout
          -u USER, --user=USER  the user name (string), mandatory
                                No user name ? You must register to MyOcean
          -p PWD, --pwd=PWD     the user password (string), mandatory
          --auth-mode=AUTH_MODE
                                the authentication mode: 'none' (for no
                                authentication), 'basic' (for basic authentication),
                                or 'cas' (for Central Authentication Service)
                                [default: cas]        
          --proxy-server=PROXY_SERVER
                                the proxy server (url)
          --proxy-user=PROXY_USER
                                the proxy user (string)
          --proxy-pwd=PROXY_PWD
                                the proxy password (string)
          -m MOTU, --motu=MOTU  the motu server to use (url), mandatory
                                Should be something like http://atoll.cls.fr/mfcglo-armor-gateway-servlet/Motu?
          -s SERVICE_ID, --service-id=SERVICE_ID
                                The service identifier (string), mandatory
                                Should be something like "http://purl.org/myocean/ontology/service/database#GLOBAL_REANALYSIS_PHYS_001_003_b-TDS"
          -d PRODUCT_ID, --product-id=PRODUCT_ID
                                The product (dataset) to download (string), mandatory
                                Should be something like "http://purl.org/myocean/ontology/product/database#dataset-armor-3d-ran-v1-myocean"
          -t DATE_MIN, --date-min=DATE_MIN
                                The min date (string following format YYYY-MM-DD)
          -T DATE_MAX, --date-max=DATE_MAX
                                The max date (string following format YYYY-MM-DD)
          -y LATITUDE_MIN, --latitude-min=LATITUDE_MIN
                                The min latitude (float in the interval [-90 ; 90])
          -Y LATITUDE_MAX, --latitude-max=LATITUDE_MAX
                                The max latitude (float in the interval [-90 ; 90])
          -x LONGITUDE_MIN, --longitude-min=LONGITUDE_MIN
                                The min longitude (float in the interval [-180 ; 180])
          -X LONGITUDE_MAX, --longitude-max=LONGITUDE_MAX
                                The max longitude (float in the interval [-180 ; 180])
          -z DEPTH_MIN, --depth-min=DEPTH_MIN
                                The min depth (float in the interval [0 ; 2e31])
          -Z DEPTH_MAX, --depth-max=DEPTH_MAX
                                The max depth (float in the interval [0 ; 2e31])
          -v VARIABLE, --variable=VARIABLE
                                The variable (list of strings), you can use netCDF variable name or standard_name attribute
                                Generic standard name table is available here:
  							  http://cf-pcmdi.llnl.gov/documents/cf-standard-names/standard-name-table/16/cf-standard-name-table.html
          -o OUT_DIR, --out-dir=OUT_DIR
                                The output dir (string), mandatory
          -f OUT_NAME, --out-name=OUT_NAME
                                The output file name (string), mandatory
                                Can be a netCDF file or a zip file containing netCDF files, depending on the server configuration
          --block-size=BLOCK_SIZE
                                The block used to download file (integer expressing bytes)
          --socket-timeout=SOCKET_TIMEOUT
                                Set a timeout on blocking socket operations (float expressing seconds)
          --user-agent=USER_AGENT
                          Set the identification string (user-agent) for HTTP
                          requests. By default this value is 'Python-urllib/x.x'
                          (where x.x is the version of the python interpreter)


REQUIRED MODULES
================

No module required.


BUGS AND QUESTIONS
==================

Please refer to the documentation for information on submitting bug reports or questions to the author.


LICENSE
=======

This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation; either version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


AUTHOR
======

CLS (Collecte Localisation Satellites) for MyOcean

www.cls.fr

operation.mis@myocean.eu.org

