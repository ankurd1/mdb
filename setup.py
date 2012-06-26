#!/usr/bin/python

from distutils.core import setup
try:
    import py2exe
except ImportError, e:
    pass

setup(name='MDB',
        version='0.8',
        description='Browse imdb data for a folder full of movies!',
        author='Ankur Dahiya',
        author_email='legalos.lotr@gmail.com',
        package_dir={'mdb':''},
        packages=['mdb'],
        windows=[{'script':'gui.py'}]
        )
