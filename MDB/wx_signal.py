#!/usr/bin/python

import wx

myEVT_FILE_DONE = wx.NewEventType()
EVT_FILE_DONE = wx.PyEventBinder(myEVT_FILE_DONE, 1)

myEVT_SHOW_MSG = wx.NewEventType()
EVT_SHOW_MSG = wx.PyEventBinder(myEVT_SHOW_MSG, 1)


class FileDoneEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, filename=None):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.filename = filename


class ShowMsgEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, content=None, html=False):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.content = content
        self.html = html
