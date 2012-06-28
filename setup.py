#!/usr/bin/python

from distutils.core import setup
try:
    import py2exe
except ImportError, e:
    pass

setup(name='MDB',
        version='0.8a',
        description='Browse imdb data for a folder full of movies!',
        author='Ankur Dahiya',
        author_email='legalos.lotr@gmail.com',
        packages=['MDB'],
        windows=[{'script':'MDB/gui.py'}],
        console=[{'script':'tools/reg-gen.py'}],
        url='http://legaloslotr.github.com/mdb',
        options = {'py2exe': {'bundle_files': 2}},
        )
