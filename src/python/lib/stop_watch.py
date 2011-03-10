#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python motu client v.${project.version} 
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

from threading import Thread, local

import time
import threading

# global stats
tsl = local()

class StopWatch(object):
    START = "start"
    END   = "end"
    LABEL = "label"
    TIME = "time"
    
    def __init__(self):
        self.timers = []
    
    def clear(self):
        self.timers = []
    
    def start(self):    
        self.timers.append( { 'label': StopWatch.START,
                              'time': time.time() })
        return self.timers[0][StopWatch.TIME]
  
    def check(self,label ):
        """Add a new check point for the current time.
           Returns the time the check point has been recorded.
        """
        self.timers.append( { 'label': label,
                              'time': time.time() })
        return self.timers[-1][StopWatch.TIME]
        
    def stop(self):
        """Stops the clock permanently for the instance of the StopWatch.
        Returns the time at which the instance was stopped.
        """
        self.timers.append( { 'label': StopWatch.END,
                              'time': time.time() })
        return self.timers[0][StopWatch.TIME]

    def elapsed(self):
        """The number of seconds since the current time that the StopWatch
        object was created.  If stop() was called, it is the number
        of seconds from the instance creation until stop() was called.
        """
        return self.__last_time() - self.__start_time()
    
    def getTimes(self):
        return self.timers
    
    def start_time(self):
        """The time at which the StopWatch instance was created.
        """
        return self.__start    
    
    def stop_time(self):
        """The time at which stop() was called, or None if stop was 
        never called.
        """
        return self.__stopped 
    
    def __last_time(self):
        """Return the current time or the time at which stop() was call,
        if called at all.
        """
        if self.timers[-1][StopWatch.LABEL] == StopWatch.END:
            return self.timers[-1][StopWatch.TIME]
        return self.__time()
    
    def __start_time(self):
        """Return the current time or the time at which stop() was call,
        if called at all.
        """
        if self.timers[0][StopWatch.LABEL] == StopWatch.END:
            return self.timers[0][StopWatch.TIME]
        return self.__time()
    
    def __time(self):
        """Wrapper for time.time() to allow unit testing.
        """
        return time.time()
    
    def __str__(self):
        """Nicely format the elapsed time
        """
        return str(self.elapsed) + ' sec'

def localThreadStopWatch():    
    if not hasattr(tsl,'timer'):
        lock = threading.Lock()
        lock.acquire()
        try:        
            if not hasattr(tsl,'timer'):
                tsl.timer = StopWatch()
        finally:
            lock.release()
    return tsl.timer