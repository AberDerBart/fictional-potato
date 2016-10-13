#!/usr/bin/python

import os
import mpd
import sys
from SleepTimer import sleepTimer

mpdHost="localhost"
mpdPort=6600




if(len(sys.argv)>=2):
	mpdHost=sys.argv[1]
elif(os.environ.get("MPD_HOST")!=None):
	mpdHost=os.environ.get("MPD_HOST")

if(len(sys.argv)>=3):
	mpdPort=sys.argv[2]

client=mpd.MPDClient()
print("Connecting to "+mpdHost+" on Port "+str(mpdPort))
client.connect(mpdHost,mpdPort)
