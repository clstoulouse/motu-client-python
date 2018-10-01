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

from threading import Thread, local

import time
import threading

# global stats
tsl = local()

class StopWatch(object):    
    TIME = "time"
    GLOBAL = "global"
    
    def __init__(self):
        # contains the computed times
        self.times = {}
        # contains the current timers
        self.timers = {}        
    
    def clear(self):
        self.timers = {}
        self.times = {}
        
    def start(self,label = GLOBAL):
        """Starts a new counter
           Returns the time the counter has been recorded.
        """
        self.timers[label] = self.__time()
        return self.timers[label]
        
    def stop(self,label=GLOBAL):
        """Stops the clock for the given counter.
        Returns the time at which the instance was stopped.
        """        
        self.times[label] = self.elapsed(label)
        del self.timers[label]
        
        return self.times[label]

    def isRunning(self, label=GLOBAL):
        return label in self.timers
        
    def elapsed(self,label=GLOBAL):
        """The number of seconds since the current time that the StopWatch
        object was created.  If stop() was called, it is the number
        of seconds from the instance creation until stop() was called.
        """
        t0 = self.times[label] if label in self.times else 0.
        t1 = self.timers[label] if label in self.timers else 0.
        t2 = self.__time() if label in self.timers else 0.
        
        return t0 + (t2 - t1)
        
    def getTimes(self):
        return self.times
          
    def __time(self):
        """Wrapper for time.time() to allow unit testing.
        """
        return time.time()
    
    def __str__(self):
        """Nicely format the elapsed time
        """
        keys = list(self.times.keys()) + [x for x in list(self.timers.keys()) if x not in list(self.times.keys())]
        txt = ""
        for key in keys:
          txt = txt + key + " : " + str(self.elapsed(key)) + " s " + ("(running)" if self.isRunning(key) else "(stopped)")+"\n"
        return txt

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
