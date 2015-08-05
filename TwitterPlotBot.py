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
from random import randint
from twython import Twython
import Image
import StringIO
from Plotter import Plotter
import os
import datetime
from time import mktime

"""
Module that creates the plot and tweets 
it for us to with the given message 
"""

# Some tweet strings
tweetStrs = [
    "the plot",
    "these are the plots you are looking for",
    "all your data belongs to us ",
    "take this graph and use it wisely",
    "what does the plot say?",
    "wow! Such graph, much color, so kool",
    "you can has the plot hoooman ",
    ]
    

class TwitterPlotBot(Thread):
    """ Blueprint for the plot bot """
    def __init__(self, apiKey, apiSecret, accessToken, accessTokenSecret, \
                 pauseCommand, resumeCommand, plotter, stopEvent, \
                 targetHandle='', tweetInterval=1000,  maxCnt=10,  \
                 dm=False):
        """ The ctor for 'PlotBot'
        apiKey, apiSecret    Your application's twitter 
        accessToken          auth credentials
        accessTokenSecret 
        pauseEvent           Toggels the tweeting
        stopEvent            Stops the tweeting (end of application)
        plotter              The plotter object that will be used to generate
                             graphs
        targetHandle         Twitter handle to be included in the tweet
        tweetInterval        Will tweet adter every 'tweetInterval'
        maxCnt               Maximum number of direct messages to be read
        dm                   Send a direct message?
        """
        super(TwitterPlotBot, self).__init__()
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.accessToken = accessToken
        self.accessTokenSecret = accessTokenSecret
        self.plotter = plotter
        self.targetHandle = targetHandle
        self.tweetInterval = tweetInterval
        #if targetHandle != "":
        #    self.dm = dm   # Do direct messaging only if we have target handle
        #else:
        #    self.dm = False
        # Sadly image upload does not seem to work (not supported by twitter API?)
        # Hence direct messaging stays disabled for now
        self.dm = False
        
        self.api = None
        self.pauseCommand = pauseCommand
        self.resumeCommand = resumeCommand
        self.stopEvent = stopEvent
        # Try and log in to twitter
        self.twitter = Twython(apiKey,apiSecret,accessToken,accessTokenSecret)
        # Start the DataLogger thread and make the plotter ready
        self.plotter.begin()
        self.keepTweeting = True     # Flag to indicate whether we want to tweet or not
        self.latestTweetCheck = datetime.datetime.utcnow()       # Used check for the latest DM 
        
        

    def __tweetPlot__(self, twtStr):
        """ This function is directly taken from the twython doc """
        photo = Image.open(self.plotter.getOutPutFileName())

        basewidth = 1000
        #wpercent = (basewidth / float(photo.size[0]))
        #height = int((float(photo.size[1]) * float(wpercent)))
        height = 500
        photo = photo.resize((basewidth, height), Image.ANTIALIAS)

        image_io = StringIO.StringIO()
        photo.save(image_io, format='PNG')

        # If you do not seek(0), the image will be at the end of the file and
        # unable to be read
        image_io.seek(0)


        response = self.twitter.upload_media(media=image_io)
        if self.dm == False:
            self.twitter.update_status(status=twtStr, media_ids=[response['media_id']])
        else:
            self.twitter.send_direct_message(screen_name=self.targetHandle, text = twtStr, 
                                              media_ids=[response['media_id']])

    def run(self):
        """ The thread that tweets updates periodically """
        while 1:
            if self.stopEvent.isSet():
                self.plotter.stop()
                return
            # Check if we need to tweet or not
            if self.targetHandle != '':
                # Get the personal message from the master
                try:
                    msgs = self.twitter.get_direct_messages(screen_id = self.targetHandle, count=10)
                except Exception, ex:
                    print "Could not receive direct messages "
                    print str(ex)
                    self.keepTweeting = True
                    continue
                    
                # Below code is to make sure that the tweet that we interpret is the latest
                if len(msgs) != 0:
                    # Check if any of the message is latest
                    temp = time.strptime(msgs[0]['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
                    temp = mktime(temp)
                    tweetTime = datetime.datetime.fromtimestamp(temp)
                    # if not, just pass
                    if tweetTime > self.latestTweetCheck:
                        for msg in msgs:
                            if msg['sender']['screen_name'].find(self.targetHandle.replace('@','')) >= 0:  # Tweet from the master
                                temp = time.strptime(msg['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
                                temp = mktime(temp)
                                tweetTime =  datetime.datetime.fromtimestamp(temp)

                                if tweetTime > self.latestTweetCheck:
                                    self.latestTweetCheck = tweetTime
                                    if msg['text'].find(self.pauseCommand) >= 0:
                                        self.keepTweeting = False
                                        print "Tweet's on hold "
                                    elif msg['text'].find(self.resumeCommand) >= 0:
                                        self.keepTweeting = True
                                        print "Tweets will be tweeted"
                            

                
            
            if self.keepTweeting:
                self.plotter.plot()
                if os.path.exists(self.plotter.getOutPutFileName()):
                    print "Tweeting........."
                    tweet = self.targetHandle + ' ' + tweetStrs[randint(0, len(tweetStrs)-1)]
                    self.__tweetPlot__(tweet)
            else:
                print "Not tweeting this cycle..."
            
            time.sleep(self.tweetInterval)

    def join(self, timeout=None):
        super(TwitterPlotBot, timeout)


def main():
    plotter = Plotter("out.png", "The plot", "some", "thing", 10, 60)
    plotter.addPlotItem("Source1", "#F01020", dataSource1)
    plotter.addPlotItem("Source2", "#201020", dataSource2)
    #plotter.begin()
    stopEvent = threading.Event()
    
    tweeter = TwitterPlotBot('api/app key', 'api/app secret',
                             'access key', 
                             'access secret',
                             '#pause', '#resume', plotter, stopEvent, '@navin_bhaskar', 500, False)
    time.sleep(120)
    print "Plotting..."
    tweeter.start()
    time.sleep(1900)
    print "Stopping it....."
    stopEvent.set()
    tweeter.join()
    #plotter.plot()
    #plotter.stop()

from random import randint
def dataSource1():
    return randint(0,9)

def dataSource2():
    return randint(0,20)
                
if __name__ == '__main__':
    main()

