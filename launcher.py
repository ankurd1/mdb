#!/usr/bin/python

import os
import sys
import sqlite3
from DBbuilder import out_dir, db_name, images_folder, DBbuilderThread,\
    create_database, is_in_db
import wx
import gui


#CONSTANTS#
movie_formats = ['avi', 'mkv', 'mp4']


#HELPER FUNCTIONS#
def setup(conn=None, cursor=None):
    print "running setup"
    os.mkdir(out_dir)
    os.mkdir(os.path.join(out_dir, images_folder))
    create_database(conn, cursor)


def is_movie_file(filename):
    if (filename[-3:] in movie_formats):
        return True
    else:
        return False


#MAIN#
if __name__ == '__main__':
    if len(sys.argv) == 1:
        # no args, use curdir
        target_files = [os.getcwd()]
    else:
        target_files = sys.argv[1:]

    # for each movie file in target_files and those one level down
    # see if in db or not
    # spawn a thread for gui and one for dbbuilder
    files_with_data = []
    files_wo_data = []

    if (not os.path.exists(out_dir)):
        setup(None, None)

    conn = sqlite3.connect(os.path.join(out_dir, db_name))
    cur = conn.cursor()

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
    app = wx.App()
    frame = gui.MyFrame(None)
    app.SetTopWindow(frame)
    frame.Maximize()

    for f in files_with_data:
        frame.add_row(f)

    db_thread = None
    if len(files_wo_data) > 0:
        db_thread = DBbuilderThread(frame, files_wo_data, '.')
        db_thread.start()

    frame.Show()
    app.MainLoop()

    if db_thread is not None:
        db_thread.join()
