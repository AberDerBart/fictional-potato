#!/bin/python
from Sleep import gotoSleep
import Scheduler
import time
import parse
import datetime
import Alarm

class Parser:
	def __init__(self,interface):
		self.scheduler=Scheduler.Scheduler()
		self.interface=interface
	def stop(self):
		self.scheduler.stop()
	def parse(self,msg):
		"""parses and executes the command given in msg"""
		args=msg.split()
		command=args[0]

		# activate sleep timer
		if(command=="sleep" and len(args)>=2):
			alarmTime=self.parseTime(args[1])

			if(alarmTime):
				self.scheduler.schedule(alarmTime,Scheduler.Job(gotoSleep,(self.interface,20),"Go to sleep"))
				return
		# add an alarm
		if(command=="alarm" and len(args)>=2):
			alarmTime=self.parseTime(args[1])

			if(len(args)>=3):
				song=msg.split(maxsplit=2)[2]
				if(int(self.interface.client.count("File",song)["songs"])==0):
					print("Parser: song not found: "+song)
					song=None
			else:
				song=None

			if(alarmTime):
				self.scheduler.schedule(alarmTime,Scheduler.Job(Alarm.alarm,(self.interface,60,song),"Alarm"))
				return
		# list scheduled items
		if(command=="list"):
			for line in str(self.scheduler).split("\n"):
				self.interface.client.sendmessage("scheduled",line)
			return
		# list scheduled items in json format
		if(command=="list_json"):
			self.interface.client.sendmessage("scheduled",self.scheduler.toJson())
			return
		if(command=="cancel" and len(args)>=2):
			index=parse.parse("{:d}",args[1])
			if(index):
				self.scheduler.cancel(index[0])
				return
		print("Error parsing string \""+msg+"\"")

	def parseTime(self,string):
		"""parses a timestamp given in [string] in the format hh:mm[:ss] or dd/MM/YYYY[ hh:mm[:ss]] or +m and returns it as datetime.datetime or None on failure"""
		# check, if a time string was given
		result=parse.parse("{:tt}",string)

		if(result):
			retn=datetime.datetime.combine(datetime.date.today(),result[0])

			# if the time already passed, increment the day
			if(retn < datetime.datetime.now()):
				retn += datetime.timedelta(days=1)
		
			return retn

		# check, if a date string was given
		result=parse.parse("{:tg}",string)

		if(result):
			return result[0]

		# check if a time offset was given
		result=parse.parse("+{:d}",string)

		if(result):
			# calculate the timestamp
			retn=datetime.datetime.now()
			retn+=datetime.timedelta(minutes=result[0])

			return retn 

		# no timestamp could be detected,
		return None
