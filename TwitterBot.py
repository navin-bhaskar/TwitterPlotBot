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

from TwitterPlotBot import TwitterPlotBot
from Plotter import Plotter
import config
import CallBacks
import time
import threading
import signal
import sys

stopEvent = threading.Event()

plotter = None
# Define the exit handler
def signalHandler(signal, frame):
        print('Exiting.....')
        stopEvent.set()
	plotter.stop()
        time.sleep(10)
        sys.exit(0)
        
# Register the exit handler        
signal.signal(signal.SIGINT, signalHandler)

def main():
    """ This is the enrty point for our application,
    "TwitterBot" """
    global plotter
    plotter = Plotter(config.config["output file"], # The output file name
                      config.config["title"],  # Title of the plot
                      config.config["xlabel"], # X axis label
                      config.config["ylabel"], # Y axis label
                      config.config["samples"], # Max number of samples to be taken
                      config.config["Log Interval"], # Log interval
                      )
                      
    # Now that we have the plotter, it is time to add items to it
    for callback in CallBacks.callbacks:
        plotter.addPlotItem(callback[0], callback[2], callback[1])
    
    

    twitterBot = TwitterPlotBot(config.config["consumer key"],
                                config.config["consumer secret"],
                                config.config["access token"],
                                config.config["access token secret"],
                                config.config["stop plot cmd"],
                                config.config["resume plot cmd"],
                                plotter,
                                stopEvent,
                                config.config["screen id"],
                                config.config["Tweet Interval"],
                                False)
    
    # Wait for some time until we have atleast one data point to plot
    time.sleep(config.config["Log Interval"])
    
    twitterBot.start()
    while True:
        pass


if __name__ == '__main__':
	main()

