#!/usr/bin/python

import sys
import os

VERSION = '0.1'

def get_platform():
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('linux'):
        return 'linux'
    else:
        return None

def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")

def module_path():
    encoding = sys.getfilesystemencoding()
    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, encoding))
    return os.path.dirname(unicode(__file__, encoding))

def debug_status():
    if ('MDB_DEBUG' in os.environ and os.environ['MDB_DEBUG'] == 'True'):
        return True
    else:
        return False
