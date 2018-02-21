#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import datetime
import multiprocessing
import os
import json
import logging
import glob
from logging.config import dictConfig
from libem import Utilities

class Config():
	UI_CLI = 0
	UI_GUI = 1
	UI_TYPE = None
	
	VERSION = '1.4.1'
	STARTTIME = time.time()
	CPU_COUNT = multiprocessing.cpu_count()
	CPU_USE = CPU_COUNT
	DEV_FLAG = False
	
	BUILD_DATETIME = datetime.datetime(
		2018, #Year
		2,  #Month
		21  #Day
	)
	
	@staticmethod
	def InitLoggers():
		# If no logs dir, make one
		if not os.path.isdir('logs'):
			os.makedirs('logs')
			
		log_config_path = Utilities.GetResource(
			'etc',
			'etc',
			'log_config.json'
		)
		
		with open(log_config_path, 'rb') as f:
			config = json.load(f)
			
		logging.config.dictConfig(config)
		
	@staticmethod
	def ClearLogs():
		if os.path.isdir('logs'):
			filelist = glob.glob("logs/*.log")
			for f in filelist:
				open(f, 'w+')
	
	@staticmethod
	def SetUiToCLI():
		Config.UI_TYPE = Config.UI_CLI
	
	@staticmethod
	def SetUiToGUI():
		Config.UI_TYPE = Config.UI_GUI
	
	@staticmethod
	def GetElapsedTime():
		return time.time() - Config.STARTTIME