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

from motu_utils import utils_configpath
import os, sys
_messages = None

MESSAGES_FILE = utils_configpath.getConfigPath() + '/messages.properties'


def _process_content(content):
    propDict = dict()
    for propLine in content:
        propDef = propLine.strip()
        if len(propDef) == 0:
            continue
        if propDef[0] in ('!', '#'):
            continue
        punctuation = [propDef.find(c) for c in ':= '] + [len(propDef)]
        found = min([pos for pos in punctuation if pos != -1])
        name = propDef[:found].rstrip()
        value = propDef[found:].lstrip(":= ").rstrip()
        propDict[name] = value

    _messages = propDict
    return _messages


def _process_file_py3(path):
    with open(path) as propFile:
        return _process_content(propFile.readlines())


def _process_file_py2(path):
    propFile = file(path, "rU")
    processed_content = _process_content(propFile)
    propFile.close()
    return processed_content


def get_external_messages():
    """Return a table of externalized messages.

    The table is lazzy instancied (loaded once when called the first time)."""
    global _messages
    if _messages is None:
        if sys.version_info > (3, 0):
            return _process_file_py3(MESSAGES_FILE)
        return _process_file_py2(MESSAGES_FILE)