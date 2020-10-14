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
import io, sys, logging

def copy(sourceHandler, destHandler, callback = None, blockSize = 65535 ):
    """Copy the available content through the given handler to another one. Process
    can be monitored with the (optional) callback function.
    
    sourceHandler: the handler through witch downloading content
    destHandler: the handler into which writing data
    callback: the callback function called for each block read. Signature: f: sizeRead -> void
    blockSize: the size of the block used to read data
    
    returns the total size read
    """
    read = 0
    while 1:
        block = sourceHandler.read(blockSize)
        if(isinstance(block, bytes)):
           exit_condition = b''
        else:
           exit_condition = ''
        if block == exit_condition:
           break
        read += len(block)
        try:
          if type(destHandler) == io.StringIO:
            if sys.version_info > (3, 0):
              destHandler.write( str(block, 'utf-8') )
            else:
              destHandler.write( unicode(block, 'utf-8') )
          else:
            destHandler.write(block)
        except Exception as inst:
          log = logging.getLogger("utils_stream:copy")
          log.error("Exception while copying remote data")
          log.error(" - Type = %s", type(inst))    # the exception instance
          if hasattr(inst, 'args'):
            log.error(" - Attributes = %s", inst.args)     # arguments stored in .args
          log.error(" - Full exception = %s", inst) 
          
        callback(read)

    return read