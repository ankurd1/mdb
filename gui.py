#!/usr/bin/python

import sys
import wx
import wx.lib.agw.ultimatelistctrl as ULC
from wx.lib.mixins.listctrl import ColumnSorterMixin
import sqlite3
from DBbuilder import out_dir, db_name, images_folder, create_database,\
        is_in_db, DBbuilderThread
import os
from textwrap import wrap
import wx_signal


#CONSTANTS#
movie_formats = ['avi', 'mkv', 'mp4']


#CLASSES#
class MyFrame(wx.Frame, ColumnSorterMixin):
    def __init__(self, parent, conn, cur, mdb_dir):
        wx.Frame.__init__(self, parent, -1, "MDB")
        self.conn = conn
        self.cur = cur
        self.mdb_dir = mdb_dir

        self.Bind(wx_signal.EVT_FILE_DONE, self.on_file_done)
        self.add_menu()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.display_width = wx.GetDisplaySize()[0]
        self.itemDataMap = {}

        self.lst = self.build_list()
        ColumnSorterMixin.__init__(self, 6)
        self.sizer.Add(self.lst, 1, wx.EXPAND)
        self.Layout()

    def build_list(self):
        lst = ULC.UltimateListCtrl(
            self, wx.ID_ANY, agwStyle=wx.LC_REPORT | wx.LC_VRULES |
            wx.LC_HRULES | wx.LC_SINGLE_SEL | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)

        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, lst)

        lst.InsertColumn(0, "Title")
        lst.InsertColumn(1, "Rating")
        lst.InsertColumn(2, "Year")
        lst.InsertColumn(3, "Genre")
        lst.InsertColumn(4, "Runtime")
        lst.InsertColumn(5, "Details")

        lst.SetColumnWidth(0, 150)
        lst.SetColumnWidth(1, 50)
        lst.SetColumnWidth(2, 50)
        lst.SetColumnWidth(3, 100)
        lst.SetColumnWidth(4, 100)
        lst.SetColumnWidth(5, -3)

        return lst

    def add_menu(self):
        menuBar = wx.MenuBar()
        menu = wx.Menu()

        m_open = menu.Append(wx.ID_ANY, "&Open Folder\tCtrl+O",
                             "Open a folder.")
        self.Bind(wx.EVT_MENU, self.open_folder, m_open)

        menuBar.Append(menu, "&File")

        menu = wx.Menu()

        m_about = menu.Append(wx.ID_ANY, "&About",
                              "Information about this program")
        self.Bind(wx.EVT_MENU, self.on_about, m_about)

        menuBar.Append(menu, "&Help")

        self.SetMenuBar(menuBar)

    def open_folder(self, evt):
        dlg = wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           | wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )

        if dlg.ShowModal() == wx.ID_OK:
            target_dir = dlg.GetPath()
        else:
            return

        dlg.Destroy()

        #create new lst
        self.itemDataMap.clear()
        self.lst.Destroy()
        self.lst = self.build_list()
        ColumnSorterMixin.__init__(self, 6)
        self.sizer.Add(self.lst, 1, wx.EXPAND)
        self.Layout()
        self.Refresh()

        # switch to this dir
        os.chdir(target_dir)

        files_with_data, files_wo_data = process_dir('.', self.conn, self.cur)

        for f in files_with_data:
            self.add_row(f)

        if len(files_wo_data) > 0:
            start_dbbuilder(self, files_wo_data, self.mdb_dir)

    def on_about(self, evt):
        print 'on_about not implemented yet'

    def GetListCtrl(self):
        return self.lst

    def OnColClick(self, event):
        event.Skip()
        self.Refresh()

    def add_row(self, filename):
        # get info from db, build info panel, add to list, update
        # itemdatamap
        data = self.get_from_db(filename)

        index = self.lst.InsertStringItem(sys.maxint, data['title'])

        self.lst.SetItemData(index, index)
        self.itemDataMap[index] = (data['title'], data['rating'], data['year'],
            data['genre'], data['runtime'], data['title'])

        self.lst.SetStringItem(index, 1, unicode(data["rating"]))
        self.lst.SetStringItem(index, 2, unicode(data["year"]))
        self.lst.SetStringItem(index, 3, unicode(data["genre"]))
        self.lst.SetStringItem(index, 4, unicode(data["runtime"]))
        self.lst.SetItemWindow(index, 5, self.build_info_panel(data),
                expand=True)

    def get_from_db(self, filename):
        res = self.cur.execute('SELECT * FROM movies WHERE filename=?',
                (filename,)).fetchall()
        return res[0]

    def build_info_panel(self, data):
        panel_3 = wx.Panel(self.lst, -1)
        img_file = os.path.join(self.mdb_dir, images_folder,
                data['filename'] + '.jpg')
        if os.path.exists(img_file):
            bmp = wx.Bitmap(img_file)
            bitmap_1 = wx.StaticBitmap(panel_3, -1, bmp)
        else:
            bitmap_1 = (100, 100)

        label_1 = wx.StaticText(panel_3, -1, self.generate_label_text(data))
        font = wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL)
        label_1.SetFont(font)

        self.label_1 = label_1

        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(bitmap_1, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        sizer_3.Add(label_1, 0, 0, 0)
        sizer_2.Add(sizer_3, 4, wx.ALIGN_CENTER_VERTICAL, 0)
        panel_3.SetSizer(sizer_2)

        return panel_3

    def generate_label_text(self, data):
        heading_width = 10
        pix_per_char = 13   # very approx value
        total_width = int((self.display_width - 500) / pix_per_char)
        print total_width
        sep = ':  '

        data2 = [('Title', unicode(data['title'])),
                ('Filename', unicode(data['filename'])),
                ('Director', unicode(data['director'])),
                ('Actors', unicode(data['actors'])),
                ('Plot', unicode(data['plot'])),
                ]

        res = ""
        for item in data2:
            item_1_lines = wrap(item[1],
                    total_width - heading_width - len(sep))
            line1 = u"{0:<{w1}}{2}{1:<{w2}}\n".format(item[0], item_1_lines[0],
                    sep, w1=heading_width, w2=total_width - heading_width - 3)
            res += line1

            for line in item_1_lines[1:]:
                out = (' ' * (heading_width + len(sep))) + line + '\n'
                res += out

        #print ''
        #print res
        return res

    def on_file_done(self, evt):
        print "event recieved containing", evt.filename
        self.add_row(evt.filename)


#HELPER FUNCTIONS#
def is_movie_file(filename):
    if (filename[-3:] in movie_formats):
        return True
    else:
        return False


def start_dbbuilder(frame, files_wo_data, mdb_dir):
    db_thread = DBbuilderThread(frame, files_wo_data, mdb_dir)
    db_thread.start()


def process_dir(directory, conn, cur):
    files_with_data = []
    files_wo_data = []

    for fil in os.listdir(directory):
        if os.path.isdir(fil):
            fil_children = os.listdir(fil)
            for c in fil_children:
                if is_movie_file(c):
                    if is_in_db(conn, cur, c):
                        files_with_data.append(c)
                    else:
                        files_wo_data.append(c)
        else:
            if is_movie_file(fil):
                if is_in_db(conn, cur, fil):
                    files_with_data.append(fil)
                else:
                    files_wo_data.append(fil)
    return files_with_data, files_wo_data


def check_and_setup():
    mdb_dir = os.path.join(os.path.expanduser('~'), out_dir)
    if (os.path.exists(mdb_dir) and\
            os.path.exists(os.path.join(mdb_dir, db_name)) and\
            os.path.exists(os.path.join(mdb_dir, images_folder))):
        conn = sqlite3.connect(os.path.join(mdb_dir, db_name))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    else:
        os.mkdir(mdb_dir)
        os.mkdir(os.path.join(mdb_dir, images_folder))
        conn = sqlite3.connect(os.path.join(mdb_dir, db_name))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        create_database(conn, cur)

    return conn, cur, mdb_dir


#MAIN#
if __name__ == '__main__':
    conn, cur, mdb_dir = check_and_setup()
    if len(sys.argv) == 1:
        # no args, use curdir
        target_files = None
    else:
        target_files = sys.argv[1:]

    if (target_files is None):
        # use cwd as target_files
        files_with_data, files_wo_data = process_dir('.', conn, cur)
    else:
        files_with_data = []
        files_wo_data = []

        #make all target_files non_absolute
        for i in range(len(target_files)):
            target_files[i] = os.path.basename(target_files[i])

        for fil in target_files:
            if os.path.isdir(fil):
                fil_children = os.listdir(fil)
                for c in fil_children:
                    if is_movie_file(c):
                        if is_in_db(conn, cur, c):
                            files_with_data.append(c)
                        else:
                            files_wo_data.append(c)
            else:
                if is_movie_file(fil):
                    if is_in_db(conn, cur, fil):
                        files_with_data.append(fil)
                    else:
                        files_wo_data.append(fil)

    print 'files_with_data', files_with_data
    print 'files_wo_data', files_wo_data

    #spawn threads
    app = wx.App(redirect=False)
    frame = MyFrame(None, conn, cur, mdb_dir)
    app.SetTopWindow(frame)
    frame.Maximize()

    for f in files_with_data:
        frame.add_row(f)

    if len(files_wo_data) > 0:
        start_dbbuilder(frame, files_wo_data, mdb_dir)

    frame.Show()
    app.MainLoop()
