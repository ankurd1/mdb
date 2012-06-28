#!/usr/bin/python

from subprocess import call
import os

MDB_EXECUTABLE = 'MDB'

def zenity_error(msg):
    call(['zenity', '--error', '--text', msg])

filePathList = os.environ['NAUTILUS_SCRIPT_SELECTED_FILE_PATHS'].splitlines()
# assuming all arguments are from cur dir only, which is true due to the
# nature of nautilus
for i in range(len(filePathList)):
    filePathList[i] = os.path.basename(filePathList[i])

try:
    if len(filePathList) == 0:
        call([MDB_EXECUTABLE])
    else:
        call_list = [MDB_EXECUTABLE]
        call_list.extend(filePathList)
        call(call_list)
except Exception, e:
    zenity_error(str(e))
