#!/usr/bin/python

import wx
from html_window import ClickableHtmlWindow
import config


class HtmlDialog(wx.Dialog):
    def __init__(self, parent, content, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, parent, *args, **kwds)
        self.SetBackgroundColour((240, 240, 240))

        self.html_panel = ClickableHtmlWindow(self)
        self.SetTitle(content['title'])
        self.html_panel.SetPage(content['body'])
        self.html_panel.attach_to_frame(parent, 0)

        self.button_1 = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.on_close)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetSize((400, 180))

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.html_panel, 1, wx.EXPAND, 0)
        sizer_1.Add(self.button_1, 0, wx.ALIGN_CENTER, 0)
        self.SetSizer(sizer_1)
        self.Layout()

    def on_close(self, evt):
        self.Destroy()


class PrefsDialog(wx.Dialog):
    def __init__(self, items_map, *args, **kwds):
        # begin wxGlade: MyDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        self.items_map = items_map
        self.controls_map = {}

        self.button_1 = wx.Button(self, -1, "OK")
        self.button_2 = wx.Button(self, -1, "Cancel")

        self.Bind(wx.EVT_BUTTON, self.on_ok, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.button_2)

        self.__set_properties()
        self.__do_layout()
        self.display_items()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyDialog.__set_properties
        self.SetTitle("Preferences - MDB")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        self.sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_4_staticbox = wx.StaticBox(self, -1, "")
        self.sizer_4_staticbox.Lower()
        self.sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.VERTICAL)
        self.sizer_1.Add(self.sizer_4, 1, wx.ALL | wx.EXPAND, 5)
        sizer_2.Add(self.button_1, 0, 0, 0)
        sizer_2.Add(self.button_2, 0, 0, 0)
        self.sizer_1.Add(sizer_2, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        self.SetSizer(self.sizer_1)
        #sizer_1.Fit(self)
        #self.Layout()
        # end wxGlade

    def on_ok(self, evt):
        for item in self.items_map:
            name = item[0]
            config.config[name] = self.controls_map[name].GetValue()

        config.config.write()
        config.post_process()
        self.Destroy()

    def on_cancel(self, evt):
        self.Destroy()

    def display_items(self):
        for item in self.items_map:
            name = item[0]
            typ = item[1]
            label = item[2]
            if (typ == 'bool'):
                checkbox = wx.CheckBox(self, -1, label)
                checkbox.SetValue(config.config[name])
                self.controls_map[name] = checkbox
                self.sizer_4.Add(checkbox, 0, wx.ALL, 5)
            elif (typ == 'str'):
                label_ctrl = wx.StaticText(self, -1, label)
                text_ctrl = wx.TextCtrl(self, -1, "")
                text_ctrl.SetMinSize((200, 27))
                text_ctrl.SetValue(str(config.config[name]))

                self.controls_map[name] = text_ctrl

                sizer = wx.BoxSizer(wx.HORIZONTAL)
                sizer.Add(label_ctrl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                        5)
                sizer.Add(text_ctrl, 0, wx.ALIGN_RIGHT |
                        wx.ALIGN_CENTER_VERTICAL, 0)

                self.sizer_4.Add(sizer, 1, wx.ALL | wx.ALIGN_RIGHT, 5)

        self.sizer_1.Fit(self)
        self.Layout()
