#!/usr/bin/python

import wx

myEVT_FILE_DONE = wx.NewEventType()
EVT_FILE_DONE = wx.PyEventBinder(myEVT_FILE_DONE, 1)

class FileDoneEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, filename=None):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.filename = filename
