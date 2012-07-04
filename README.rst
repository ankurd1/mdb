MDB (MovieDirBrowser)
=====================

MDB is a cool way to visualize your movie collection and decide which movie to
watch next! Run MDB on a folder or a set of files/folders and it downloads imdb 
data for all movie files found and shows it in a nice GUI.

You can then sort the movies by title, rating, runtime, releaseYear or Genre.
All this data is cached on your computer, so we don't need to hit imdb
the next time!

MDB runs on Windows and Linux.

For more details and downloads, visit the `website <http://legaloslotr.github.com/mdb>`_.

Acknowlegements
---------------

All the data about movies is downloaded from `IMDB <http://imdb.com>`_, using
the awesome API at `imdbapi.com <http://imdbapi.com>`_.

The GUI is developed using `wxPython <http://wxpython.org>`_.

MDB also uses `requests <https://github.com/kennethreitz/requests>`_ and
`configobj <http://www.voidspace.org.uk/python/configobj.html>`_.
