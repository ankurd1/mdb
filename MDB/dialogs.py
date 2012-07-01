#!/usr/bin/python

import wx
from html_window import ClickableHtmlWindow
from lib import VERSION

class AboutDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetBackgroundColour((240, 240, 240))
        self.html_panel = ClickableHtmlWindow(self)
        self.set_html_content(self.html_panel)
        self.button_1 = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.on_close)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("About MDB")
        self.SetSize((400, 180))

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.html_panel, 1, wx.EXPAND, 0)
        sizer_1.Add(self.button_1, 0, wx.ALIGN_RIGHT, 0)
        self.SetSizer(sizer_1)
        self.Layout()

    def set_html_content(self, panel):
        abt_dlg_content = '''
        <body bgcolor="#f1f1f1">
        <center>
        <h2>MDB - MovieDirBrowser</h2>
        v{0}<br>
        <a href="http://legaloslotr.github.com/mdb">
        http://legaloslotr.github.com/mdb</a><br>
        Data collected from <a href="http://imdb.com">IMDB</a>
        </center></body>
        '''.format(VERSION)
        panel.SetPage(abt_dlg_content)

    def on_close(self, evt):
        self.Destroy()
