#!/usr/bin/python

from TwitterPlotBot import TwitterPlotBot
from Plotter import Plotter
import config
import CallBacks
import time
import threading
import signal

stopEvent = threading.Event()

# Define the exit handler
def signalHandler(signal, frame):
        print('Exiting.....')
        stopEvent.set()
        time.sleep(10)
        sys.exit(0)
        
# Register the exit handler        
signal.signal(signal.SIGINT, signalHandler)

def main():
    """ This is the enrty point for our application,
    "TwitterBot" """
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

