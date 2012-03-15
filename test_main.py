#!/usr/bin/python

import mdb

def test_name_parser():
    movies = [('Die Welle[2008]DvDrip[Ger]-FXG', 'die welle'),
            ('J.Edgar[2011]BRRip XviD-ETRG', 'j edgar')]

    for filename, moviename in movies:
        assert(mdb.get_movie_name(filename) == moviename)
