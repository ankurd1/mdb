#!/usr/bin/python

import DBbuilder
import wx
import os
import shutil

movies1 = [('Die Welle[2008]DvDrip[Ger]-FXG.avi', 'die welle', True),
        ('J.Edgar[2011]BRRip XviD-ETRG.avi', 'j edgar', True),
        ('The Descendants[2011]DVDRip XviD-ETRG.avi', 'the descendants', True),
        ('Columbus.Circle.2012.DVDRiP.XviD-SiC.avi', 'columbus circle', True),
        ('Jaane.Tu...Ya.Jaane.Na.2008.DVDRip-SaM.avi', 'jaane tu ya jaane na', True),
        ('Band Baaja Baaraat - DVDRip - XviD - 1CDRip - [DDR].avi',
            'band baaja baaraat', False),
        ('percy jackson & the olympians- the lightning thief (2010)' +
        'dvdrip .mkv', 'percy jackson & the olympians the lightning thief', True),
        ('Serenity[2005][Aka.Firefly]DvDrip[Eng]-aXXo.avi', 'serenity', True),
        ('(500)Days of Summer.[2009].RETAIL.DVDRIP.XVID.[Eng]-DUQA.avi',
            '500 days of summer', True),
        ('Into the Wild.avi', 'into the wild', True),
        ('The.Incredibles[2004]DvDrip[Eng]-spencer.avi', 'the incredibles', True),
        ]

movies2 = [('social network', ('The Social Network', '2010')),
        ('die welle', ('The Wave', '2008'))]


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

    dbthread = DBbuilder.DBbuilderThread(None, [item[0] for item in movies1], '.')
    dbthread.start()
    dbthread.join()

    for item in movies1:
        if item[2]:
            assert(os.path.exists(os.path.join('.mdb', 'images', item[0] + '.jpg')))
        else:
            assert(True)
