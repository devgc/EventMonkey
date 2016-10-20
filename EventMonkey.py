#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import argparse
import logging
import multiprocessing

#From https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking

if sys.platform.startswith('win'):
    # First define a modified version of Popen.
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    # Second override 'Popen' class with our modified version.
    forking.Popen = _Popen

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
        help=u'Name to prepend to output files'
    )
    
    arguements.add_argument(
        '-p','--path',
        dest='events_path',
        required=True,
        action="store",
        type=unicode,
        help=u'Path to Event Files'
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
        '--esconfig',
        dest='esconfig',
        action="store",
        type=unicode,
        default=None,
        help='Elastic YAML Config File'
    )
    arguements.add_argument(
        '--esurl',
        dest='esurl',
        action="store",
        type=unicode,
        default=None,
        help='Elastic RFC-1738 URL'
    )
    arguements.add_argument(
        '--eshost',
        dest='eshost',
        action="store",
        type=str,
        default=None,
        help='Elastic Host IP'
    )
    arguements.add_argument(
        '--esuser',
        dest='esuser',
        action="store",
        type=str,
        default=None,
        help='Elastic Host User'
    )
    arguements.add_argument(
        '--espass',
        dest='espass',
        action="store",
        type=unicode,
        default=None,
        help='Elastic Password [if not supplied, will prompt]'
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