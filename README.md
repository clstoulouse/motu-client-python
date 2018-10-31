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
You must use python version 2.7.X or later.  
This program is fully compatible with Python 3.X versions.  
There is two methods to install the client, by using PIP or from a tar.gz file.  
 [setuptools](#InstallationSetuptools) python package has be installed in order to display the motuclient version successfully.    
  
## <a name="InstallationPIP">Using PIP</a>
Python Package Index is used to ease installation.  
If your host needs a PROXY set it, for example:  
```
export HTTPS_PROXY=http://myCompanyProxy:8080  
```  

Then run:  
  
```
pip install motuclient  
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

# <a name="Configuration">Configuration</a>  
All parameters can be defined as command line options or can be written in a configuration file.
The configuration file is a .ini file. This file is located in the following directory:  

* on __Unix__ platforms: $HOME/motuclient/motuclient-python.ini
* on __Windows__ platforms: %USERPROFILE%\motuclient\motuclient-python.ini
  
The expected structure of file is:  
``` 
[Main]  
user=john  
pwd=secret  
log_level=10  
proxy_server=proxy.domain.net:8080  
proxy_user=john  
proxy_pwd=secret  
motu=http://motu-ip-server:port/motu-web/Motu
product_id=dataset-psy2v3-pgs-med-myocean-bestestimate  
date_min=2010-11-08 12:00:00  
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
* __-p PWD, --pwd=PWD__ the user password (string) for the specified authentication mode. Special characters can be used.  
  * __Example 1__ From a Windows batch, if your password contains a percent character, double the percent character: If password is CMS2017@%! then enter -u username-p CMS2017@%%! 
  * __Example 2__ From a Windows batch, if your password contains a space character, set password between double quotes: If password is CMS2017 @%! then enter -u username-p "CMS2017 @%%!"
  * __Example 3__ From a Linux shell, if your password contains a space character, set password between simple quotes: If password is CMS2017 @%! then enter -u username-p 'CMS2017 @%!'

* __-m MOTU, --motu=MOTU__ Motu server url, e.g. "-m http://localhost:8080/motu-web/Motu"  
* __-s SERVICE_ID, --service-id=SERVICE_ID__ The service identifier (string), e.g. -s Mercator_Ocean_Model_Global-TDS  
* __-d PRODUCT_ID, --product-id=PRODUCT_ID__ The product (data set) to download (string), e.g. -d dataset-mercator-psy4v3-gl12-bestestimate-uv  
* __-t DATE_MIN, --date-min=DATE_MIN__ The min date with optional hour resolution (string following format YYYY-MM-DD [HH:MM:SS]), e.g. -t "2016-06-10" or -t "2016-06-10 12:00:00". Be careful to not forget double quotes around the date.     
* __-T DATE_MAX, --date-max=DATE_MAX__ The max date with optional hour resolution (string following format YYYY-MM-DD  [HH:MM:SS ]), e.g. -T "2016-06-11" or -T "2016-06-10 12:00:00".  Be careful to not forget double quotes around the date.      
* __-y LATITUDE_MIN, --latitude-min=LATITUDE_MIN__ The min latitude (float in the interval  [-90 ; 90 ]), e.g. -y -80.5  
* __-Y LATITUDE_MAX, --latitude-max=LATITUDE_MAX__ The max latitude (float in the interval  [-90 ; 90 ]), e.g. -Y 80.5   
* __-x LONGITUDE_MIN, --longitude-min=LONGITUDE_MIN__ The min longitude (float in the interval [-180 ; 180 ]), e.g. -x -180      
* __-X LONGITUDE_MAX, --longitude-max=LONGITUDE_MAX__ The max longitude (float in the interval  [-180 ; 180 ]), e.g. -X 35.5      
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

* __--block-size=BLOCK_SIZE__ The block used to download file (integer expressing bytes)  
* __--socket-timeout=SOCKET_TIMEOUT__ Set a timeout on blocking socket operations (float expressing seconds)  
* __--user-agent=USER_AGENT__ Set the identification string (user-agent) for HTTP requests. By default this value is 'Python-urllib/x.x' (where x.x is the version of the python interpreter)  
  
  
# <a name="UsageExamples">Usage examples</a>   
In the following examples, variable ${MOTU\_USER} and ${MOTU\_PASSWORD} are user name and user password used to connect to the CAS server for single sign on.  
${MOTU\_SERVER\_URL} is the URL on the MOTU HTTP(s) server. For example http://localhost:8080/motu-web/Motu.  
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

