#!/usr/bin/python

import os
import sys
import sqlite3
from DBbuilder import out_dir, db_name, images_folder, DBbuilderThread
from gui import GuiThread
import wx
import gui

movie_formats = ['avi', 'mkv', 'mp4']


def setup(conn=None, cursor=None):
    print "running setup"
    os.mkdir(out_dir)
    os.mkdir(os.path.join(out_dir, images_folder))
    create_database(conn, cursor)


def create_database(conn=None, cursor=None):
    if conn is None:
        conn = sqlite3.connect(os.path.join(out_dir, db_name))
        cursor = conn.cursor()

    cursor.execute('''CREATE TABLE movies (
            filename TEXT,
            title TEXT,
            year INTEGER,
            released TEXT,
            genre TEXT,
            rating REAL,
            runtime TEXT,
            director TEXT,
            actors TEXT,
            plot TEXT,
            poster TEXT
            )''')
    cursor.execute('CREATE UNIQUE INDEX filename_index ON movies (filename)')
    conn.commit()


def is_movie_file(filename):
    if (filename[-3:] in movie_formats):
        return True
    else:
        return False


def is_in_db(conn, cur, filename):
    if conn is None:
        return False
    else:
        res = cur.execute('SELECT * FROM movies WHERE filename=?',
                (filename,)).fetchall()
        if len(res) > 0:
            return True
        else:
            return False

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
