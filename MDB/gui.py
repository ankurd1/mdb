#!/usr/bin/python

import sys
import wx
import wx.lib.agw.ultimatelistctrl as ULC
from wx.lib.mixins.listctrl import ColumnSorterMixin
import sqlite3
from DBbuilder import out_dir, db_name, images_folder, create_database,\
        is_in_db, DBbuilderThread, movie_formats
import os
from textwrap import wrap
import wx_signal
import shutil
import wx.html
from html_window import ClickableHtmlWindow
from lib import module_path

#RESOURCES#
imdb_icon = os.path.join(module_path(), 'resources/images/imdb-logo.png')

#CLASSES#
class MyFrame(wx.Frame, ColumnSorterMixin):
    def __init__(self, parent, conn, cur, mdb_dir):
        wx.Frame.__init__(self, parent, -1, "MDB")
        self.conn = conn
        self.cur = cur
        self.mdb_dir = mdb_dir

        self.Bind(wx_signal.EVT_FILE_DONE, self.on_file_done)
        self.add_menu()
        self.add_sb()
        self.total_rows = 0

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.display_width = wx.GetDisplaySize()[0]
        self.itemDataMap = {}

        self.lst = self.build_list()
        ColumnSorterMixin.__init__(self, 6)
        self.sizer.Add(self.lst, 1, wx.EXPAND)
        self.Layout()

    def add_sb(self):
        sb = wx.StatusBar(self)
        self.sb = sb
        sb.SetStatusText("0 Files")
        self.SetStatusBar(sb)

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

        lst.SetColumnWidth(0, 100)
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
        self.total_rows = 0
        self.update_sb()
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
        self.total_rows += 1
        self.update_sb()

    def update_sb(self):
        if (self.total_rows == 1):
            self.sb.SetStatusText("1 File")
        else:
            self.sb.SetStatusText("{0} Files".format(self.total_rows))

    def get_from_db(self, filename):
        res = self.cur.execute('SELECT * FROM movies WHERE filename=?',
                (filename,)).fetchall()
        return res[0]

    def build_info_panel(self, data):
        html_win = ClickableHtmlWindow(self.lst, size=(-1, 180))
                #style=wx.html.HW_SCROLLBAR_NEVER)

        html_text = "<table><tr>"
        img_file = os.path.join(self.mdb_dir, images_folder,
                data['filename'] + '.jpg')
        if os.path.exists(img_file):
            html_text += '<td width="100" rowspan="2">\
                    <img src="{0}"></td>\n'.format(img_file)
        else:
            html_text += '<td width="100" rowspan="2"></td>'

        # imdb icon
        html_text += '<td><a href="http://imdb.com/title/{0}">\
                <img src="{1}"></a></td></tr>'.format(data['imdbID'], imdb_icon)

        # details
        html_text += "<tr><td>" + self.generate_label_text(data) + "</td></tr>"
        html_text += "</table>"
        
        html_win.SetPage(html_text)

        return html_win

    def make_wrappable(self, txt):
        wrap_points = ['.', '-', ']', ')']
        for point in wrap_points:
            txt = txt.replace(point, point + ' ')
        return txt

    def generate_label_text(self, data):
        data2 = [('Title', unicode(data['title'])),
                ('Filename', self.make_wrappable(unicode(data['filename']))),
                ('Director', unicode(data['director'])),
                ('Actors', unicode(data['actors'])),
                ('Plot', unicode(data['plot'])),
                ]

        res = u"<table cellspacing=0 cellpadding=2>"
        for item in data2:
            res += u'<tr valign="top"><td valign="top"><b>{0}</b></td>\
                    <td valign="top">{1}</td></tr>\n'.\
                    format(item[0], item[1])

        res += u"</table>"
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
        if os.path.isdir(os.path.join(directory, fil)):
            fil_children = os.listdir(os.path.join(directory, fil))
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
        try: shutil.rmtree(mdb_dir)
        except: pass
        os.mkdir(mdb_dir)
        os.mkdir(os.path.join(mdb_dir, images_folder))
        conn = sqlite3.connect(os.path.join(mdb_dir, db_name))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        create_database(conn, cur)

    return conn, cur, mdb_dir

#MAIN#
def main():
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

        #target_files should be in cwd
        #make all target_files non_absolute
        for i in range(len(target_files)):
            target_files[i] = os.path.basename(target_files[i])

        for fil in target_files:
            if os.path.isdir(fil):
                f_with, f_wo = process_dir(fil, conn, cur)
                files_with_data.extend(f_with)
                files_wo_data.extend(f_wo)
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
    frame.Layout()
    app.MainLoop()

if __name__ == '__main__':
    main()
