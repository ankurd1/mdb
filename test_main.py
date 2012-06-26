#!/usr/bin/python

import DBbuilder
import wx
import os
import shutil
import wx_signal
from gui import MyFrame
from gui import setup as db_dir_setup


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
    if os.path.exists('.mdb'):
        shutil.rmtree('.mdb')

    db_dir_setup()

    dbthread = DBbuilder.DBbuilderThread(None, [item[0] for item in movies1],
            '.')
    dbthread.start()
    dbthread.join()

    for item in movies1:
        if item[2]:
            assert(os.path.exists(os.path.join('.mdb', 'images',
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
    if os.path.exists('.mdb'):
        shutil.rmtree('.mdb')

    db_dir_setup()

    app = wx.App(False)
    frame = CountingFrame(None, total=len(movies1))

    dbthread = DBbuilder.DBbuilderThread(frame, [item[0] for item in movies1],
            '.')
    dbthread.start()

    app.MainLoop()


def test_gui_row_addition():
    app = wx.App()
    frame = MyFrame(None)
    app.SetTopWindow(frame)
    frame.Maximize()

    for f in movies1:
        frame.add_row(f[0])

    frame.Show()
    print frame.label_1.GetLabel()
    app.MainLoop()
