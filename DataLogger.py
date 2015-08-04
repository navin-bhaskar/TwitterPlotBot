#!/usr/bin/python


#  
#  (c) Navin Bhaskar <navin.bhaskar.5@gmail.com>
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#  
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the  nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  

import threading
from threading import Thread
import time
import datetime


class DataObject(object):
    """ A data type represnting the data"""
    def __init__(self, data, time):
        self.data = data
        self.time = time
    
class DataLogger(Thread):
    """ A generic data logger that will keep calling a user supplied
    function to get the data and stop "N" number of entries.
    The data item fetched is stored in a list with certain capacity
    once this number "N" is reached, older entries make way for new entries.
    This object also time stamps each of the entry.
    """
    
    def __init__(self, cbMethod, N, interval, stopEvent):
        """
        This is the constructor for this class which initialize various
        data structures 
        
        cbMethod    supplied call back method that will be called to get the data
        N           number of entries to record
        interval    Time interval after which the data is to be logged 
        stopEvent   Event that is to be raised to stop this thread
        
        """
        super(DataLogger, self).__init__()
        self.cbMethod = cbMethod
        self.maxCnt = N
        self.interval = interval
        self.stopEvent = stopEvent
        
        self.dataList = []           # this is "the" data list
        self.lock = threading.Lock() # one for the sync

    def run(self):
        """ The heart beat of this thread; keeps logging data at "intervals" """
        
        while 1:
            if self.stopEvent.isSet():
                return
            
            try:
                dat = self.cbMethod()
            except Exception as ex:
                print "You did not give me what I was expecting. \
                This function expects a function or, you're function \
                did not handle an exception "
                raise ex
            
            if type(dat) != type([]):
                raise AttributeError, "The callback function was to return a list, but did not"
            
            tempData = DataObject(dat, datetime.datetime.now())

            # lock the access to dataList
            
            self.lock.acquire()
            if len(self.dataList) < self.maxCnt:
                self.dataList.append(tempData)    # space in "dataList", add item
            else:
                self.dataList = self.dataList[1:] # List full, remove first element
                self.dataList.append(tempData)    # and append new data
            self.lock.release()
            
            print "Logged: ",
            print tempData.data
            
            time.sleep(self.interval)

    def getDataList(self):
        """ 
        Returns the dataList logged until the time this function was 
        called
        """
        self.lock.acquire()
        data = self.dataList
        self.lock.release()
        
        # Put the data in below format
        # Time data_0_0
        # Time data_0_1
        # ....
        # Time data_1_0
        # Time data_1_1
        # ....

        theList = []
        #if (len(data) == 0):
        #    return []
        
        if (len(data) == 0):
            return []       # Nothing has been recorded yet, return 
        n = len(data[0].data)
        for dat in data:
            temp = dat.data
            for i in range(0, n):
                if (i < len(theList)):
                    theList[i].append(DataObject(temp[i], dat.time))
                else:
                    theList.append([])
                    theList[i].append(DataObject(temp[i], dat.time))

        return theList

    def join(self, timeout=None):
        """ For the times when you want to join this thread
        with the "main" """
        super(DataLogger, self).join(timeout)

        
def dataGetter():
    """ The "data" that we want to log """
    from random import randint
    return [randint(0,9), randint(0,10), randint(0,11)]

def main():
    event = threading.Event()
    i=0
    dl = DataLogger(dataGetter, 10, 5, event)
    print "Starting the data logger thread "
    dl.start()
    
    while i < 20:
        print "The list..."
        temp = dl.getDataList()

        for data in temp:
            #print "Data is ",
            #print data
            print "-------------------------------"
            for dat in data:
                print "The data: ",
                print dat.data,
                print "Time["+ str(dat.time) +"]"
            print "-----------------------------"
        i += 1
        time.sleep(5)

    event.set()    
    dl.join()


if __name__ == '__main__':
    main()
    
