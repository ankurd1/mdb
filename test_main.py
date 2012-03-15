#!/usr/bin/python

import mdb

def test_name_parser():
    movies = [('Die Welle[2008]DvDrip[Ger]-FXG.avi', 'die welle'),
            ('J.Edgar[2011]BRRip XviD-ETRG.avi', 'j edgar'),
            ('The Descendants[2011]DVDRip XviD-ETRG.avi', 'the descendants'),
            ('Columbus.Circle.2012.DVDRiP.XviD-SiC.avi', 'columbus circle'),
            ('Jaane.Tu...Ya.Jaane.Na.2008.DVDRip-SaM.avi', 'jaane tu ya jaane na'),
            ('Band Baaja Baaraat - DVDRip - XviD - 1CDRip - [DDR].avi', 'band baaja baaraat'),
            ('percy jackson & the olympians- the lightning thief (2010) dvdrip .mkv',
                'percy jackson & the olympians the lightning thief'),
            ('Serenity[2005][Aka.Firefly]DvDrip[Eng]-aXXo.avi', 'serenity'),
            ('(500)Days of Summer.[2009].RETAIL.DVDRIP.XVID.[Eng]-DUQA.avi', '500 days of summer'),
            ('Into the Wild.avi', 'into the wild'),
            ('The.Incredibles[2004]DvDrip[Eng]-spencer.avi', 'the incredibles'),
            ]

    for filename, moviename in movies:
        assert(mdb.get_movie_name(filename) == moviename)
