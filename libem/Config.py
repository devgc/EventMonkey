#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import datetime
import multiprocessing
import os
import json
import logging
from logging.config import dictConfig

class Config():
	UI_CLI = 0
	UI_GUI = 1
	UI_TYPE = None
	
	VERSION = '1.0.2'
	STARTTIME = time.time()
	CPU_COUNT = multiprocessing.cpu_count()
	CPU_USE = CPU_COUNT
	DEV_FLAG = False
	
	BUILD_DATETIME = datetime.datetime(
		2016, #Year
		8,  #Month
		8  #Day
	)
	
	@staticmethod
	def InitLoggers(path='etc/log_config.json'):
		# Make sure logdir exists#
		if not os.path.exists('logs'):
			os.makedirs('logs')
			
		if os.path.exists(path):
			with open(path, 'rb') as f:
				config = json.load(f)
			logging.config.dictConfig(config)
		else:
			raise Exception('No json log configuration file found at: {}'.format(path))
	
	@staticmethod
	def SetUiToCLI():
		Config.UI_TYPE = Config.UI_CLI
	
	@staticmethod
	def SetUiToGUI():
		Config.UI_TYPE = Config.UI_GUI
	
	@staticmethod
	def GetElapsedTime():
		return time.time() - Config.STARTTIME