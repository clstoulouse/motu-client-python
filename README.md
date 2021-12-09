# Motu Client Python Project 
@author Product owner <tjolibois@cls.fr>  
@author Scrum master, software architect <smarty@cls.fr>  
@author Quality assurance, continuous integration manager <smarty@cls.fr>  

>How to read this file? 
Use a markdown reader: 
plugins [chrome](https://chrome.google.com/webstore/detail/markdown-preview/jmchmkecamhbiokiopfpnfgbidieafmd?utm_source=chrome-app-launcher-info-dialog) exists (Once installed in Chrome, open URL chrome://extensions/, and check "Markdown Preview"/Authorise access to file URL.), 
or for [firefox](https://addons.mozilla.org/fr/firefox/addon/markdown-viewer/)  (anchor tags do not work)
and also plugin for [notepadd++](https://github.com/Edditoria/markdown_npp_zenburn).

>Be careful: Markdown format has issue while rendering underscore "\_" character which can lead to bad variable name or path.


# Summary
* [Overview](#Overview)
* [Build](#Build)
* [Installation](#Installation)
    * [Prerequisites](#InstallationPre)
    * [Using PIP](#InstallationPIP)
    * [From tar.gz file](#InstallationTGZ)
* [Configuration](#Configuration)
* [Usage and options](#Usage)
    * [Usage from PIP installation](#UsagePIP)
    * [Usage from tar.gz installation](#UsageTGZ)
* [Usage examples](#UsageExamples)
    * [Download](#UsageExamplesDownload)
    * [GetSize](#UsageExamplesGetSize)	
    * [DescribeProduct](#UsageExamplesDescribeProduct)
* [Licence](#Licence)
* [Troubleshooting](#Troubleshooting)
    * [Unable to download the latest version watched on GitHub from PIP](#Troubleshooting)  
    * [From Windows, Parameter error](#TroubleshootingWinArgErr)

# <a name="Overview">Overview</a>
Motu client "motuclient-python" is a python script used to connect to Motu HTTP server in order to:  

* __extract__ the data of a dataset, with geospatial, temporal and variable criterias (default option)   
* __get the size__ of an extraction with geospatial, temporal and variable criterias  
* __get information__ about a dataset  

This program can be integrated into a processing chain in order to automate the downloading of products via the Motu.  
  
  
# <a name="Build">Build</a>  
From the root folder runs the command:  
  
```
./patchPOMtoBuild.sh  
mvn clean install -Dmaven.test.skip=true
[...]
[INFO] BUILD SUCCESS
[...]
```  

This creates two archives in the target folder:

* motuclient-python-$version-$buildTimestamp-src.tar.gz: Archive containing all the source code
* motuclient-python-$version-$buildTimestamp-bin.tar.gz: Archive ready to be installed



# <a name="Installation">Installation</a> 

## <a name="InstallationPre">Prerequisites</a>
Since motuclient release version 3.X.Y, you must use python version 3.7.10 or later.  
__/!\__ motuclient does not work with the OpenSSL library release 1.1.1.e. Either use an older version such as the 1.1.1.d or jump to the 1.1.1.f release.  
There are two methods to install the client, by using PIP or from a tar.gz file.  
 [setuptools](#InstallationSetuptools) python package has be installed in order to display the motuclient version successfully.    
  
## <a name="InstallationPIP">Using PIP</a>
Python Package Index is used to ease installation.  
If your host needs a PROXY set it, for example:  
```
export HTTPS_PROXY=http://myCompanyProxy:8080  
```  

Then run:  
  
```
pip install motuclient --upgrade  
```
  
Now "motuclient" is installed, you can [configured it](#Configuration) and [use it](#UsagePIP).
  
  
## <a name="InstallationTGZ">From tar.gz file</a>
Deploy the archive (file motuclient-python-$version-bin.tar.gz available from [GitHub release](https://github.com/clstoulouse/motu-client-python/releases)) in the directory of your choice.  
```  
tar xvzf motuclient-python-$version-$buildTimestamp-bin.tar.gz
```  

Create a [configuration file](#Configuration) and set the user and password to use to connect to the CAS server.   

## <a name="InstallationSetuptools">Install setuptools python package</a>
"[Setuptools](https://pypi.python.org/pypi/setuptools)" python package has to be installed in order to display the version with option --version, here is how to install it:    
 
If your host needs a PROXY set it, for example:  
```
export HTTPS_PROXY=http://myCompanyProxy:8080  
```  

Then run:  

```  
sudo apt install python-pip  
pip install --upgrade setuptools  
```  

# <a name="Configuration">Configuration file</a>  

All parameters can be defined as command line options or can be written in a configuration file.  
The configuration file is a .ini file, encoded in UTF-8 without BOM. This file is located in the following directory:  

* on __Unix__ platforms: $HOME/motuclient/motuclient-python.ini
* on __Windows__ platforms: %USERPROFILE%\motuclient\motuclient-python.ini
  
The expected structure of file is:  
``` 
[Main]  
# Motu credentials  
user=john  
pwd=secret  

motu=http://motu-ip-server:port/motu-web/Motu  
service_id=GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS   
product_id=global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh  
date_min=2019-03-27  
date_max=2019-03-27  
latitude_min=-30  
latitude_max=40.0  
longitude_min=-10  
longitude_max=179.9166717529297    
depth_min=0.493    
depth_max=0.4942  
# Empty or non set means all variables  
# 1 or more variables separated by a coma and identified by their standard name  
variable=sea_water_potential_temperature,sea_surface_height_above_geoid 
# Accept relative or absolute path. The dot character "." is the current folder  
out_dir=./out_dir  
out_name=test.nc  

# Logging
# https://docs.python.org/3/library/logging.html#logging-levels  
# log_level=X {CRITICAL:50, ERROR:40, WARNING:30, INFO:20, DEBUG:10, TRACE:0}   
log_level=0   

# block_size block used to download file (integer expressing bytes) default=65535
# block_size=65535  
socket_timeout=120000  

# Http proxy to connect to Motu server
# proxy_server=proxy.domain.net:8080  
# proxy_user=john  
# proxy_pwd=secret  
``` 

A configuration file in another location can be specified by the `--config-file` option. It is even possible to split the configuration into two or more files. This is useful, for example, to keep server configuration in one file and dataset configuration in another:
```  
./motuclient.py --config-file ~/server.ini --config-file ~/mercator.ini
``` 
If by chance there is a parameter listed in both configuration files, the value in the last file (e.g. `mercator.ini`) is the one actually used.

Note that the password must be encoded in UTF-8.  
If it contains UTF-8 special characters, on Windows host only, you only have to double the "percent" character. If password is CMS2017@%! then enter   

```  
pwd = CMS2017@%%! 
```  

Example of server.ini on Windows host only, with user password is   
__Password__:  
```  
loginForTesting2 &~#"'{([-|`_\^@)]=}¨^£$ µ*§!/:.;?,%<>  
```  

__server.ini__:  
```  
[Main]
user = loginForTesting2@groupcls.com
pwd = loginForTesting2 &~#"'{([-|`_\^@)]=}¨^£$ µ*§!/:.;?,%%<>
auth-mode = cas
motu = http://motuURL:80/motu-web/Motu
out_dir = J:/dev/CMEMS-CIS-MOTU/git/motu-validkit/output/04-python-client/MOTU-208
```  

Example of server.ini on Linux host only, with user password is   
__Password__:
```  
loginForTesting2 &~#"'{([-|`_\^@)]=}¨^£$ µ*§!/:.;?,%<>  
```  

__server.ini__:
```   
[Main]
user = loginForTesting2@groupcls.com
pwd = loginForTesting2 &~#"'{([-|`_\^@)]=}¨^£$ µ*§!/:.;?,%<>
auth-mode = cas
motu = http://motuURL:80/motu-web/Motu
out_dir = J:/dev/CMEMS-CIS-MOTU/git/motu-validkit/output/04-python-client/MOTU-208
```  

# <a name="Usage">Usage</a>  
Starts the motu python client.  

## <a name="UsagePIP">Usage from PIP installation</a>  
Since version 1.8.0:  
```  
motuclient -h  
motuclient [options]
```  
Before version 1.8.0:  
```  
python -m motu-client -h  
python -m motu-client [options]
```  
  
[Options](#UsageOptions) are listed below.  
Method to used when it has been installed with [PIP method](#InstallationPIP).  


## <a name="UsageTGZ">Usage from tar.gz installation</a>  
```  
./motuclient.py  -h  
motuclient.py [options]
```  
Method to used when it has been installed with [tar.gz method](#InstallationTGZ).  
Usefull if host is offline and has no Internet access.

### <a name="UsageOptions">__Options:__</a>  


* __-h, --help__            show this help message and exit  
* __-q, --quiet__           print logs with level WARN in stdout, used to prevent any output in stdout  
* __--noisy__               print logs with level TRACE in stdout  
* __--verbose__             print logs with level DEBUG in stdout  
* __--version__             show program's version number and exit, [setuptools](#InstallationSetuptools) python package has be installed to run it successfully    

* __--proxy-server=PROXY_SERVER__ Proxy server (url) used to contact Motu 
* __--proxy-user=PROXY_USER__ Proxy user name (string)
* __--proxy-pwd=PROXY_PWD__ Proxy password (string)  

* __--auth-mode=AUTH_MODE__  the authentication mode: [default: cas]  
  * __none__ for no authentication
  * __basic__ for basic authentication
  * __cas__ for Central Authentication Service  
* __-u USER, --user=USER__  User name (string) for the specified authentication mode
* __-p PWD, --pwd=PWD__ User password (string) for the specified authentication mode. UTF8 special characters can be used but contraints depending of your operating system must be applyied:

  * __Windows__ users, be careful if your password contain once of the following characters:
    * __percent__: From a Windows batch command, if your password contains a percent character, double the percent character: If password is CMS2017@%! then enter   
    
    ```
    -u username-p CMS2017@%%! 
    ```  

    * __space__: From a Windows batch command, if your password contains a space character, set password between double quotes: If password is CMS2017 @%! then enter  
    
    ```
    -u username-p "CMS2017 @%%!"
    ```  
  
  
    * __double quotes__: From a Windows batch command, if your password contains a double quotes character, double the double quotes character: If password is CMS2017"@%! then enter  
    
    ```
    -u username-p "CMS2017""@%%!"
    ```  
  
  * __Linux__ users, be careful if your password contain once of the following characters:
    * __space__: From a Linux bash shell command, if your password contains a space character, set password between double quotes: If password is CMS2017 @% then enter  
    
    ```
    -u username-p "CMS2017 @%"
    ```  
  
    * __exclamation point__: From a Linux bash shell command, if your password contains an exclamation point character, cut the password in two double quotes strings, and append the exclamation point between simple quote: If password is CMS!2017@% then enter  
    
    ```
    -u username-p "CMS"'!'"2017@%" 
    ```  
  
    * __double quotes__: From a Linux bash shell command, if your password contains a double quotes character, escape the double quotes character by prefixing it with backslash: If password is CMS2017"@% then enter  
    
    ```
    -u username-p "CMS2017\"@%"
    ```  

    * __grave accent__: From a Linux bash shell command, if your password contains a grave accent character, escape the grave accent character by prefixing it with backslash: If password is CMS2017`@% then enter  
    
    ```
    -u username-p "CMS2017\`@%"
    ``` 
  
* __-m MOTU, --motu=MOTU__ Motu server url, e.g. "-m http://localhost:8080/motu-web/Motu"  
* __-s SERVICE_ID, --service-id=SERVICE_ID__ The service identifier (string), e.g. -s Mercator_Ocean_Model_Global-TDS  
* __-d PRODUCT_ID, --product-id=PRODUCT_ID__ The product (data set) to download (string), e.g. -d dataset-mercator-psy4v3-gl12-bestestimate-uv  
* __-t DATE_MIN, --date-min=DATE_MIN__ The min date with optional hour resolution (string following format YYYY-MM-DD [HH:MM:SS]), e.g. -t "2016-06-10" or -t "2016-06-10 12:00:00". Be careful to not forget double quotes around the date.     
* __-T DATE_MAX, --date-max=DATE_MAX__ The max date with optional hour resolution (string following format YYYY-MM-DD  [HH:MM:SS ]), e.g. -T "2016-06-11" or -T "2016-06-10 12:00:00".  Be careful to not forget double quotes around the date.      
* __-y LATITUDE_MIN, --latitude-min=LATITUDE_MIN__ The min latitude (float in the interval  [-90 ; 90 ]), e.g. -y -80.5  
* __-Y LATITUDE_MAX, --latitude-max=LATITUDE_MAX__ The max latitude (float in the interval  [-90 ; 90 ]), e.g. -Y 80.5   
* __-x LONGITUDE_MIN, --longitude-min=LONGITUDE_MIN__ The min longitude (float), e.g. -x -180      
* __-X LONGITUDE_MAX, --longitude-max=LONGITUDE_MAX__ The max longitude (float), e.g. -X 355.5      
* __-z DEPTH_MIN, --depth-min=DEPTH_MIN__ The min depth (float in the interval  [0 ; 2e31 ] or string 'Surface'), e.g. -z 0.49  
* __-Z DEPTH_MAX, --depth-max=DEPTH_MAX__ The max depth (float in the interval  [0 ; 2e31 ] or string 'Surface'), e.g. -Z 0.50
* __-v VARIABLE, --variable=VARIABLE__ The variable (list of strings), e.g. -v salinity -v sst  
* __-S, --sync-mode__ Sets the download mode to synchronous (not recommended). If this parameter is set, Motu server is called with parameter [console](https://github.com/clstoulouse/motu#download-product). Otherwise
, Motu server is called with parameter [status](https://github.com/clstoulouse/motu#download-product).   


* __-o OUT_DIR, --out-dir=OUT_DIR__ The output dir where result (download file) is written (string). If it starts with "console", behaviour is the same as with --console-mode.       
* __-f OUT_NAME, --out-name=OUT_NAME__ The output file name (string)  
* __--console-mode__ Write result on stdout. In case of an extraction, write the nc file http URL where extraction result can be downloaded. In case of a getSize or a describeProduct request, display the XML result.

* __-D, --describe-product__ Get all updated information on a dataset. Output is in XML format, [API details](https://github.com/clstoulouse/motu#describe-product)  
* __--size__ Get the size of an extraction. Output is in XML format, [API details](https://github.com/clstoulouse/motu#get-size)

* __--block-size=BLOCK_SIZE__ The block used to download file (integer expressing bytes), default=65535 bytes  
* __--socket-timeout=SOCKET_TIMEOUT__ Set a timeout on blocking socket operations (float expressing seconds)  
* __--user-agent=USER_AGENT__ Set the identification string (user-agent) for HTTP requests. By default this value is 'Python-urllib/x.x' (where x.x is the version of the python interpreter)  
* __--outputWritten=OUTPUT_FORMAT__ Set the output format (file type) of the returned file for download requests. By default this value is 'netcdf' and no other value is supported.  
  
  
# <a name="UsageExamples">Usage examples</a>   

In the following examples, variable ${MOTU\_USER} and ${MOTU\_PASSWORD} are user name and user password used to connect to the CAS server for single sign on.  
${MOTU\_SERVER\_URL} is the URL on the MOTU HTTP(s) server, for example http://localhost:8080/motu-web/Motu.  
Commands "./motuclient.py" has to be replaced by "python -m motuclient" if it has been installed with [PIP method](#UsagePIP).  


## <a name="UsageExamplesDownload">Download</a>  

### Download and save extracted file on the local machine
This command writes the extraction result data in file: /data/test.nc  

```  
./motuclient.py --verbose --auth-mode=none -m ${MOTU_SERVER_URL} -s HR_MOD_NCSS-TDS -d HR_MOD -z 0.49 -Z 0.50 -x -70 -X 25 -y -75 -Y 10 -t "2016-06-10" -T "2016-06-11" -v salinity -o /data -f test.nc
``` 

### Display on stdout the HTTP(s) URL of the NC file available on the Motu server
The HTTP(s) URL is displayed on stdout. This URL is a direct link to the file which is available to be downloaded.  

```  
./motuclient.py --quiet --auth-mode=cas -u ${MOTU_USER} -p ${MOTU_PASSWORD}  -m ${MOTU_SERVER_URL} -s HR_MOD_NCSS-TDS -d HR_MOD -z 0.49 -Z 0.50 -x -70 -X 25 -y -75 -Y 10 -t "2016-06-10" -T "2016-06-11" -v salinity -o console
``` 

## <a name="UsageExamplesGetSize">GetSize</a>  
See [https://github.com/clstoulouse/motu#ClientAPI_GetSize](https://github.com/clstoulouse/motu#ClientAPI_GetSize) for more details about XML result.  

### Get the XML file which contains the extraction size on the local machine
```  
./motuclient.py --size --auth-mode=cas -u ${MOTU_USER} -p ${MOTU_PASSWORD}  -m ${MOTU_SERVER_URL} -s HR_MOD_NCSS-TDS -d HR_MOD -z 0.49 -Z 0.50 -x -70 -X 25 -y -75 -Y 10 -t "2016-06-10" -T "2016-06-11" -v salinity -o /data -f getSizeResult.xml
``` 

### Display the extraction size as XML on stdout
```  
./motuclient.py --quiet --size --auth-mode=cas -u ${MOTU_USER} -p ${MOTU_PASSWORD}  -m ${MOTU_SERVER_URL} -s HR_MOD_NCSS-TDS -d HR_MOD -z 0.49 -Z 0.50 -x -70 -X 25 -y -75 -Y 10 -t "2016-06-10" -T "2016-06-11" -v salinity -o console
``` 


## <a name="UsageExamplesDescribeProduct">DescribeProduct</a>  
See [https://github.com/clstoulouse/motu#describe-product](https://github.com/clstoulouse/motu#describe-product) for more details about XML result.  

### Get the XML file which contains the dataset description on the local machine
```  
./motuclient.py -D --auth-mode=cas -u ${MOTU_USER} -p ${MOTU_PASSWORD}  -m ${MOTU_SERVER_URL} -s HR_MOD_NCSS-TDS -d HR_MOD -o /data -f describeProductResult.xml
``` 

### Display the dataset description XML result on stdout
```  
./motuclient.py --quiet -D --auth-mode=cas -u ${MOTU_USER} -p ${MOTU_PASSWORD}  -m ${MOTU_SERVER_URL} -s HR_MOD_NCSS-TDS -d HR_MOD -o console
``` 




# <a name="Licence">Licence</a> 
This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation; either version 2.1 of the License, or (at your option) any later version.  
  
This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.  
  
You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.  

# <a name="Troubleshooting">Troubleshooting</a>  
# <a name="TroubleshootingPIPCache">Unable to download the latest version watched on GitHub from PIP</a>
Example:  
```  
pip install motuclient  
Collecting motuclient  
  Using cached https://test-files.pythonhosted.org/packages/4a/7d/41c3bdd973baf119371493c193248349c9b7107477ebf343f3889cabbf48/motuclient-X.Y.Z.zip  
Installing collected packages: motuclient  
  Running setup.py install for motuclient ... done  
Successfully installed motuclient-X.Y.Z  
```  
  
Clear your PIP cache: On Windows, delete the folder %HOMEPATH%/pip. On archlinux pip cache is located at ~/.cache/pip.
After re run the command:  
```  
pip install motuclient  
Collecting motuclient  
  Using https://test-files.pythonhosted.org/packages/4a/7d/41c3bdd973baf119371493c193248349c9b7107477ebf343f3889cabbf48/motuclient-X.Y.Z.zip  
Installing collected packages: motuclient  
  Running setup.py install for motuclient ... done  
Successfully installed motuclient-X.Y.Z  
``` 

# <a name="TroubleshootingWinArgErr">From Windows, Parameter error</a>
From Windows, the command "motuclient.py --version" returns an error.  
10:44:24 [ERROR] Execution failed: [Excp 13] User (option 'user') is mandatory when 'cas' authentication is set. Please provide it.

__Analyse:__  
This issue comes from the fact that Windows command line does not pass parameters to python command.  
  
__Solution:__  
``` 
Edit the Windows Registry Key "HKEY_CLASSES_ROOT\py_auto_file\shell\open\command" and append at the end of the value %*  
Exemple: "C:\dvltSoftware\python\Python27\python.exe" "%1" %*  
``` 

# <a name="TroubleshootingPythonVersionErr">Error on all motuclient commands</a>
For example the command "motuclient.py --version" returns this kind of error:  
``` 
Traceback (most recent call last):
  File "C:\dvlt\python\python2.7.18\Scripts\motuclient-script.py", line 11, in <module>
    load_entry_point('motuclient==3.0.0.post1', 'console_scripts', 'motuclient')()
  File "c:\dvlt\python\python2.7.18\lib\site-packages\motuclient\motuclient.py", line 352, in main
    initLogger()
  File "c:\dvlt\python\python2.7.18\lib\site-packages\motuclient\motuclient.py", line 336, in initLogger
    logging.addLevelName(utils_log.TRACE_LEVEL, 'TRACE')
AttributeError: 'module' object has no attribute 'TRACE_LEVEL'
``` 

__Analyse:__  
This issue comes from a too old python installation version.  You must use Python 3.7.10 or higher.  
  
__Solution:__  
Find and install the Python 3 distribution for your operating system.  