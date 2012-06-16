#!/usr/bin/python

import sys

import wx
import wx.lib.agw.ultimatelistctrl as ULC
from wx.lib.mixins.listctrl import ColumnSorterMixin
import sqlite3
from DBbuilder import out_dir, db_name, images_folder
import os


class MyFrame(wx.Frame, ColumnSorterMixin):

    def connect_to_db(self):
        self.conn = sqlite3.connect(os.path.join(out_dir, db_name))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def __init__(self, parent):

        wx.Frame.__init__(self, parent, -1, "MDB")
        self.connect_to_db()

        # Build the list
        self.itemDataMap = {}

        self.list = ULC.UltimateListCtrl(self, wx.ID_ANY,
                agwStyle=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES |
                wx.LC_SINGLE_SEL | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.list)
        ColumnSorterMixin.__init__(self, 5)

        self.list.InsertColumn(0, "Title")
        self.list.InsertColumn(1, "Rating")
        self.list.InsertColumn(2, "Year")
        self.list.InsertColumn(3, "Genre")
        self.list.InsertColumn(4, "Runtime")
        self.list.InsertColumn(5, "Details")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()

    def GetListCtrl(self):
        return self.list

    def OnColClick(self, event):
        event.Skip()
        self.Refresh()

    def add_row(self, filename):
        # get info from db, build info panel, add to list, update
        # itemdatamap
        data = self.get_from_db(filename)

        index = self.list.InsertStringItem(sys.maxint, data['title'])

        list.SetItemData(index, index)
        self.itemDataMap[index] = (data['title'], data['rating'], data['year'],
                data['genre'], data['runtime'])

        list.SetStringItem(index, 1, data["rating"])
        list.SetStringItem(index, 2, data["year"])
        list.SetStringItem(index, 3, data["genre"])
        list.SetStringItem(index, 4, data["runtime"])
        list.SetItemWindow(index, 5, self.build_info_panel(data), expand=True)

    def get_from_db(self, filename):
        res = self.cursor.execute('SELECT * FROM movies WHERE filename=?',
                filename).fetchall()
        return res[0]

    def build_info_panel(self, data):
        panel_3 = wx.Panel(self.list, -1)
        bitmap_1 = wx.StaticBitmap(panel_3, -1, wx.Bitmap(os.path.join(
            out_dir, images_folder, data['filename'] + '.jpg'),
            wx.BITMAP_TYPE_ANY))
        label_1 = wx.StaticText(panel_3, -1, self.generate_label_text(data),
            style=wx.ALIGN_CENTRE)

        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(bitmap_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_3.Add(label_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_2.Add(sizer_3, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        panel_3.SetSizer(sizer_2)

        return panel_3

    def generate_label_text(self, data):
        text = \
            "Title:\t\t{0}\n" +\
            "Filename:\t\t{1}\n" +\
            "Actors:\t\t{2}\n" +\
            "Director:\t\t{3}\n" +\
            "Plot:\t\t{4}\n"
        text.format(data['title'], data['filename'], data['actors'],
            data['director'], data['plot'])

        return text

app = wx.App()

frame = MyFrame(None)
app.SetTopWindow(frame)
frame.Show()

app.MainLoop()
