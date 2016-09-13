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

# SI unit prefixes
SI_K, SI_M, SI_G, SI_T = 10 ** 3, 10 ** 6, 10 ** 9, 10 ** 12

def convert_bytes(n):
    """Converts the given bytes into a string with the most appropriate
    unit power.
    
    Note that prefixes like M, G, T are power of 10 (ISO/IEC 80000-13:2008) and
    not power of 2."""        
    if   n >= SI_T:
        return '%.1f TB' % (float(n) / SI_T)
    elif n >= SI_G:
        return '%.1f GB' % (float(n) / SI_G)
    elif n >= SI_M:
        return '%.1f MB' % (float(n) / SI_M)
    elif n >= SI_K:
        return '%.1f kB' % (float(n) / SI_K)
    else:
        return '%d B' % n
