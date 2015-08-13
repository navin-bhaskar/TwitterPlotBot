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

import os
import re
import threading
from DataLogger import DataLogger
import time
import subprocess


class PlotItem:
    """ A class to hold the plot items """
    def __init__(self, itemName, itemColor, itemCb):
        """
        itemName    Name that would appear in the graph
        itemColor   Plot color
        itemCb      call back method for this item
        """
        if (type(itemName) != type("")):
            raise ValueError, "itemName should be a string "

        self.name = itemName
        self.itemCb   = itemCb
        self.color = itemColor

class Plotter:
    """ 
    This class is responsible for plotting all the 
    data items in the list to a file in png format using 
    gnuplot 
    
    """

    def __init__(self, outputFileName, title, xlabel, ylabel, N, interval, gnuplot = "gnuplot"):
        """ The ctor 
        
        outputFileName   The file name with which the png file is to be created
        title            Title of the plot
        xlabel           X axis label
        ylabel           Y axis label
        N                number of data objects to get in
        interval         Interval at which the data is to captured
        gnuplot          The gnuplot program, on windows env, supply the complete path
        
        """
        if (type(title) != type('') or
            type(xlabel) != type('') or
            type(ylabel) != type('')):
            raise ValueError, "This function expects 'title', 'xlabel' and 'ylabel' all to \
            be strings"
        
        if (type(interval) != type(1) or
            type(N) != type(1) ):
            raise ValueError, "This function requires both 'interval' and 'N' to be of integer type"
        
        if (type(gnuplot) != type('')):
            raise ValueError, "Path to gnuplot must be a string"
        
        self.gnuplot = gnuplot
        self.plotItems = []    # will hold all the plot items 
        self.stopEvent = threading.Event()
        self.n = N
        self.interval = interval
        self.DataLogger = None
        self.out = outputFileName

        self.reRgb = re.compile(r'#[a-fA-F0-9]{6}$')
    
        

        self.gnuplotScript = """
        set term png size 1000,500
        set output [output_here]
        set xlabel [xlabel_here]
        set ylabel [ylabel_here]
        set xdata time
        set timefmt "%b-%d-%H:%M:%S"
        set grid
        """

        self.gnuplotScript = self.gnuplotScript.replace('[output_here]', "'"+outputFileName+"'")
        self.gnuplotScript = self.gnuplotScript.replace('[xlabel_here]', "'"+xlabel+"'")
        self.gnuplotScript = self.gnuplotScript.replace('[ylabel_here]', "'"+ylabel+"'")
        
        self.tempScript = ""

    def addPlotItem(self, itemName, itemColor, itemCb):
        """ This will add items to our "plotItems" list
        and when it is time to get the data, this list will be walked through 
        
        itemName    Name of the item as it appears in the graph 
        itemColor   Color with this data item is to be plotted, in hexadecimal format
        itemCb      Call back function for this item that will supply the data
        
        Note: This has to be called before calling the "begin" function
        """
        if not self.reRgb.match(itemColor):
            raise ValueError, "Not a valid RGB color code"



            
        self.plotItems.append(PlotItem(itemName, itemColor, itemCb))
    
    def __theCallBack__(self):
        """ The call back method, which will execute all the callback functions in the
        list and will aggregate the data """
        dataList = []

        for plotItem in self.plotItems:
            try:
                temp = plotItem.itemCb()
            except Exception as ex:
                raise ex # "One of the call back function has failed "

            if (type(temp) != type(1) and type(temp) != type(1.1)):
                raise ValueError, "The function %s should return an int or a float type"  %plotItem.itemCb.__name__

            dataList.append(temp)

        # Return the data list that we have to the logger
        return dataList

    def begin(self):
        """ Starts the logger thread """
        if self.DataLogger == None:
            self.DataLogger = DataLogger(self.__theCallBack__, self.n, self.interval, self.stopEvent)
            self.DataLogger.start()

    def stop(self):
        """ Stop the logging thread """
        self.stopEvent.set()
        try:
            if DataLogger != None:
                print "Stopping the datalogger "
                self.DataLogger.join()
            self.DataLogger = None
        except:
            pass
        self.tempScript = ""
        
    def __del__(self):
        self.stop()

    def getOutPutFileName(self):
        return self.out
        
    def __addToGnuPlotCmdColorTitle__(self, color, title):
        """ Internal method that will add plot title and color """
        if self.tempScript.find("plot") < 0:
            self.tempScript = self.tempScript + "\nplot "
        
        self.tempScript = self.tempScript + "'-' using 1:2 with lines title '%s' lt rgb '%s', " %(title, color)   

    def __addToGnuPlotCmdDataTime__(self, data, time):
        """ Add the date and time information """
        self.tempScript = self.tempScript + "\n%s %s" %(time, data)

    def __addToGnuPlotCmdEOD__(self):
        """ Add end of data """
        self.tempScript = self.tempScript + "\ne\n"
        
    def __addToGnuPlotCmdXRange__(self, startTime, endTime):
        """ Set the start and end time """
        start = startTime.strftime("%b-%d-%H:%M:%S")
        end = endTime.strftime("%b-%d-%H:%M:%S")
        self.tempScript = self.gnuplotScript
        self.tempScript = self.tempScript + """\nset xrange ["%s":"%s"]\n""" %(start, end)
        self.tempScript = self.tempScript + r'set format x "%H:%M\n%b-%d'
        
    def plot(self):
        """ This method will get the recorded data and plots
        it to png file using gnuplot """
        recordedList = self.DataLogger.getDataList()

        if len(recordedList) == 0:
            return -1      # No records 
            
        
        n = len(self.plotItems)
        # Set the x axis range 
        temp = len(recordedList[0])
        startTime = recordedList[0][0].time
        endTime = recordedList[0][temp-1].time
        self.__addToGnuPlotCmdXRange__(startTime, endTime)

        for j in range (0, n):
            self.__addToGnuPlotCmdColorTitle__(self.plotItems[j].color, self.plotItems[j].name)
        i=0    
        for record in recordedList:
            # Now, add all the data points for gnuplot to chew on 
            for rec in record:
                timeData = rec.time.strftime("%b-%d-%H:%M:%S")
                data = str(rec.data)
                self.__addToGnuPlotCmdDataTime__(data, timeData)

            self.__addToGnuPlotCmdEOD__()
            i = i+1
        #print self.tempScript
        plot = subprocess.Popen([self.gnuplot], stdin=subprocess.PIPE)
        plot.communicate(self.tempScript)
        print self.tempScript
        self.tempScript = ""

    
def main():
    plotter = Plotter("out.png", "The plot", "some", "thing", 10, 60)
    plotter.addPlotItem("Source1", "#F01020", dataSource1)
    plotter.addPlotItem("Source2", "#201020", dataSource2)
    plotter.begin()
    time.sleep(120)
    print "Plotting..."
    plotter.plot()

    time.sleep(1600)
    plotter.plot()
    plotter.stop()

from random import randint
def dataSource1():
    return randint(0,9)

def dataSource2():
    return randint(0,20)
                
if __name__ == '__main__':
    main()
           
                
            

            
        
