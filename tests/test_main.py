#!/usr/bin/python

import sys
import os
sys.path.append(os.path.abspath(".."))
import MDB.DBbuilder as DBbuilder
import wx
import shutil
import MDB.wx_signal as wx_signal
from MDB.gui import MyFrame
from MDB.gui import check_and_setup
from MDB.DBbuilder import images_folder


#DATA#
movies1 = [('Die Welle[2008]DvDrip[Ger]-FXG.avi', 'die welle', True),
        ('J.Edgar[2011]BRRip XviD-ETRG.avi', 'j edgar', True),
        ('The Descendants[2011]DVDRip XviD-ETRG.avi', 'the descendants', True),
        ('Columbus.Circle.2012.DVDRiP.XviD-SiC.avi', 'columbus circle', True),
        ('Jaane.Tu...Ya.Jaane.Na.2008.DVDRip-SaM.avi', 'jaane tu ya jaane na',
            True),
        ('Band Baaja Baaraat - DVDRip - XviD - 1CDRip - [DDR].avi',
            'band baaja baaraat', False),
        ('percy jackson & the olympians- the lightning thief (2010)' +
        'dvdrip .mkv', 'percy jackson & the olympians the lightning thief',
        True),
        ('Serenity[2005][Aka.Firefly]DvDrip[Eng]-aXXo.avi', 'serenity', True),
        ('(500)Days of Summer.[2009].RETAIL.DVDRIP.XVID.[Eng]-DUQA.avi',
            '500 days of summer', True),
        ('Into the Wild.avi', 'into the wild', True),
        ('The.Incredibles[2004]DvDrip[Eng]-spencer.avi', 'the incredibles',
            True),
        ]

movies2 = [('social network', ('The Social Network', '2010')),
        ('die welle', ('The Wave', '2008'))]

movie_filenames = ['Die Welle[2008]DvDrip[Ger]-FXG.avi',
    'J.Edgar[2011]BRRip XviD-ETRG.avi']
#SETUP FUNCTIONS#
def setup_db_dir():
    try: shutil.rmtree('test')
    except: pass
    os.mkdir('test')

    home_var = 'HOME'
    if (home_var not in os.environ):
        home_var = 'USERPROFILE'
    home_old = os.environ[home_var]
    os.environ[home_var] = os.path.abspath('./test')
    conn, cur, mdb_dir = check_and_setup()

    os.environ[home_var] = home_old

    return conn, cur, mdb_dir

#TEST CASES#
def test_name_parser():
    for filename, moviename, _ in movies1:
        assert(DBbuilder.get_movie_name(filename) == moviename)


def test_get_imdb_data_correctness():
    for moviename, data in movies2:
        res = DBbuilder.get_imdb_data(moviename)
        assert((res['Title'], res['Year']) == data)


def test_get_imdb_data_existence():
    for filename, moviename, _ in movies1:
        res = DBbuilder.get_imdb_data(moviename)
        assert(res is not None)
        print ""
        print filename, '->', res['Title'], res['Year'], res['Genre']


def test_dbbuilder_images():
    conn, cur, mdb_dir = setup_db_dir()

    dbthread = DBbuilder.DBbuilderThread(None, [item[0] for item in movies1],
            mdb_dir)
    dbthread.start()
    dbthread.join()

    for item in movies1:
        if item[2]:
            assert(os.path.exists(os.path.join(mdb_dir, images_folder,
                item[0] + '.jpg')))
        else:
            assert(True)


class CountingFrame(wx.Frame):
    def __init__(self, parent, total):
        wx.Frame.__init__(self, parent, title="Test", size=(300, 300))
        self.Bind(wx_signal.EVT_FILE_DONE, self.on_file_done)
        self.total = total

    def on_file_done(self, evt):
        print "event recieved containing" + evt.filename
        self.total -= 1
        assert True
        if self.total == 0:
            self.Destroy()


def test_DBbuilder_signal():
    conn, cur, mdb_dir = setup_db_dir()

    app = wx.App(False)
    frame = CountingFrame(None, total=len(movies1))

    dbthread = DBbuilder.DBbuilderThread(frame, [item[0] for item in movies1],
            mdb_dir)
    dbthread.start()

    app.MainLoop()


def test_gui_row_addition():
    conn, cur, mdb_dir = setup_db_dir()

    app = wx.App()
    frame = MyFrame(None, conn, cur, mdb_dir)
    app.SetTopWindow(frame)
    frame.Maximize()
    frame.Show()

    dbthread = DBbuilder.DBbuilderThread(frame, [item[0] for item in movies1],
            mdb_dir)
    dbthread.start()

    app.MainLoop()
