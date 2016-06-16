#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import argparse
import logging
import multiprocessing

import libem.WindowsEventManager as WindowsEventManager
import libem.Config as Config

Config.Config.InitLoggers()
Config.Config.SetUiToCLI()

MAIN_LOGGER = logging.getLogger('Main')

def GetArguements():
    '''Get needed options for processesing'''
    usage = '''EventMonkey (A Windows Event Parsing Utility)'''
    
    arguements = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(usage)
    )
    
    arguements.add_argument(
        '-n','--evidencename',
        dest='evidencename',
        required=True,
        action="store",
        type=unicode,
        help='Path to Event Files'
    )
    
    arguements.add_argument(
        '-p','--path',
        dest='events_path',
        required=True,
        action="store",
        type=unicode,
        help='Path to Event Files'
    )
    
    arguements.add_argument(
        '-o','--output_path',
        dest='output_path',
        required=True,
        action="store",
        type=unicode,
        help='Output Path'
    )
    
    arguements.add_argument(
        '--threads',
        dest='threads_to_use',
        action="store",
        type=int,
        default=Config.Config.CPU_COUNT,
        help='Number of threads to use (default is all [{}])'.format(Config.Config.CPU_COUNT)
    )
    
    arguements.add_argument(
        '--eshost',
        dest='eshost',
        action="store",
        type=str,
        default=None,
        help='Elastic Host IP'
    )
    
    return arguements

def Main():
    multiprocessing.freeze_support()
    ###GET OPTIONS###
    arguements = GetArguements()
    options = arguements.parse_args()
    
    manager = WindowsEventManager.WindowsEventManager(
        options
    )
    manager.ProcessEvents()

if __name__ == '__main__':
    Main()