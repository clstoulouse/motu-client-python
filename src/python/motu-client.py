#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Deprecated
# Only for retrocompatibility of Motu <= v1.7
import logging
import motuclient

deprecatedWarnMsg='"motu-client" module is deprecated since version1.8. A new Python module named "motuclient" without a dash separator between motu and client shall be used instead of "motu-client".'
motuclient.initLogger()
motuclient.log.warn( deprecatedWarnMsg )    


def get_client_version():
    #motuclient.log.warn( deprecatedWarnMsg + 'e.g. motuclient.get_client_version()')    
    return motuclient.get_client_version()

def get_client_artefact():
    #motuclient.log.warn( deprecatedWarnMsg + ', e.g. motuclient.get_client_artefact()')  
    return motuclient.get_client_artefact()

def main():
    #motuclient.log.warn( deprecatedWarnMsg + ', e.g. motuclient.main()')  
    motuclient.main()

if __name__ == '__main__':
    #motuclient.log.warn( deprecatedWarnMsg + ', e.g. motuclient.main()')  
    motuclient.main()