#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import multiprocessing
from multiprocessing.managers import BaseManager
from Config import Config
import progressbar
from progressbar import ProgressBar,Bar,Percentage,AnimatedMarker,Counter

PROGRESS_LOGGER = logging.getLogger('ProgressManager')

class ProcessingStatisticsClass():
    '''Store Processing Statistics for Processes Across Threads'''
    def __init__ (self):
        pass

class ProgressBarClass():
    def __init__(self,interface_type,count=None,description=None):
        self.interface_type = interface_type
        self.current_value = 0
        
        if self.interface_type == Config.UI_CLI:
            widgets = []
            
            if description is not None:
                widgets.append('{}: '.format(description))
            
            if count is not None:
                widgets.append(Percentage())
                widgets.append(' ')
                widgets.append(Bar())
            else:
                widgets.append(Counter())
                widgets.append(' ')
                widgets.append(AnimatedMarker(markers='.oO@* '))
                
            if count is not None:
                self.progressBar = ProgressBar(widgets=widgets, max_value=count)
            else:
                self.progressBar = ProgressBar(max_value=progressbar.UnknownLength,widgets=widgets)
        else:
            PROGRESS_LOGGER.error('interface type not handled: {}'.format(self.interface_type))
            raise Exception('interface type not handled: {}'.format(self.interface_type))
        
    def SetValue(self,value):
        if self.interface_type == Config.UI_CLI:
            self.current_value = value
            self.progressBar.update(self.current_value)
        else:
            PROGRESS_LOGGER.error('interface type not handled: {}'.format(self.interface_type))
            raise Exception('interface type not handled: {}'.format(self.interface_type))
        
    def Increment(self,increment):
        if self.interface_type == Config.UI_CLI:
            self.current_value+=increment
            try:
                self.progressBar.update(self.current_value)
            except:
                pass
        else:
            PROGRESS_LOGGER.error('interface type not handled: {}'.format(self.interface_type))
            raise Exception('interface type not handled: {}'.format(self.interface_type))
        
    def Finish(self):
        if self.interface_type == Config.UI_CLI:
            self.progressBar.finish()
            
    def Close(self):
        if self.interface_type == Config.UI_CLI:
            pass
        
class ProgressManager(BaseManager):
    value = 0

ProgressManager.register('ProgressBar', ProgressBarClass)
