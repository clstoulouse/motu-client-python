import os
import sys

from setuptools import setup, find_packages

# project libraries path
LIBRARIES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'python')

# Manage imports of project libraries
if not os.path.exists(LIBRARIES_PATH):
    sys.stderr.write('\nERROR: can not find project libraries path: %s\n\n' % os.path.abspath(LIBRARIES_PATH))
    sys.exit(1)
sys.path.append(LIBRARIES_PATH)

from motu_utils import pom_version

setup(
    name='motuclient',
    version=pom_version.getPOMVersion(),
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
    author_email='smarty@cls.fr',
    platforms=['any'],

    url='https://github.com/clstoulouse/motu-client-python',
    license='LGPL',

    package_dir = {'': 'src/python', 'motu_utils': 'src/python/motu_utils'},
    packages=['motu_utils'],
    py_modules = ['motuclient', 'motu-client'],
    include_package_data=True,

    download_url='https://github.com/clstoulouse/motu-client-python/releases/',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Topic :: Scientific/Engineering :: GIS',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: OS Independent'
    ],

    entry_points={
        'console_scripts': [
            'motuclient = motuclient:main'
        ]
    }
)
