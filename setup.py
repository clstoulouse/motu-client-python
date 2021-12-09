import os

from setuptools import setup, find_packages
from xml.etree import ElementTree


def getPOMVersion():
    version = "unknown"
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)

    try:
        # For production tree, while run from cur folder
        version = __getPOMVersion(os.path.join(dname, "..", "pom.xml"))
    except Exception:
        # For development tree
        version = __getPOMVersion(os.path.join(dname, "pom.xml"))
    finally:
        return version


def __getPOMVersion(POM_FILE):
    namespaces = {'xmlns': 'http://maven.apache.org/POM/4.0.0'}
    tree = ElementTree.parse(POM_FILE)
    root = tree.getroot()
    version = root.find("xmlns:version", namespaces=namespaces)
    return str(version.text)


setup(
    name='motuclient',
    version=getPOMVersion(),
    python_requires='>=2.7',
    description='Extract and download gridded data through a python command line from Motu web server. Used in CMEMS context http://marine.copernicus.eu/',
    long_description='Motu is a high efficient and robust Web Server which fills the gap between heterogeneous data providers to end users. Motu handles, extracts and transforms oceanographic huge volumes of data without performance collapse. This client enables to extract and download data through a python command line.',
    keywords=[
        'Copernicus',
        'CMEMS',
        'CLS',
        'Motu',
        'motuclient-python',
        'Dissemination Unit'
    ],

    author='Sylvain MARTY, CLS',
    author_email='smarty@groupcls.com',
    platforms=['any'],

    url='https://github.com/clstoulouse/motu-client-python',
    license='LGPL',

    package_dir = {'': 'src', 'motuclient': 'src/motuclient', 'motu_utils': 'src/motuclient/motu_utils'}, 
    packages = ['motuclient', 'motu_utils'],
    py_modules = ['motuclient'],
    include_package_data=True,

    download_url='https://github.com/clstoulouse/motu-client-python/releases/',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Topic :: Scientific/Engineering :: GIS',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: OS Independent'
    ],

    entry_points={
        'console_scripts': [
            'motuclient = motuclient.motuclient:main',
            'motu-client = motuclient.motuclient:main'
        ]
    },

    install_requires=['python-dateutil']
)
