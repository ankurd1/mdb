#!/usr/bin/python

import urllib2
import os
from subprocess import call
import sys
import sqlite3
import wx_signal
import wx
import re
import threading

try:
    import simplejson as json
except ImportError, e:
    import json


#CONSTANTS#
api_url = 'http://www.imdbapi.com/?t='
api_extra_opts = '' #'&plot=full'
out_dir = '.mdb'
db_name = 'mdbdata.sqlite'
images_folder = 'images'
movie_formats = ['avi', 'mkv', 'mp4', 'm4v', 'rmvb']
#http_proxy = 'proxy22.iitd.ac.in:3128'
#https_proxy = 'proxy22.iitd.ac.in:3128'
http_proxy = None
https_proxy = None
img_size = '100'


#HELPER FUNCTIONS#
def zenity_error(msg):
    try:
        call(['zenity', '--error', '--text', msg])
    except OSError, e:
        # zenity not available
        # print to stderr
        sys.stderr.write(msg + '\n')


def create_database(conn, cur):
    cur.execute('''CREATE TABLE movies (
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
    cur.execute('CREATE UNIQUE INDEX filename_index ON movies (filename)')
    conn.commit()


def add_to_db(filename, file_data, conn, cur):
    cur.execute('INSERT INTO movies VALUES(?,?,?,?,?,?,?,?,?,?,?)', (
        filename, file_data['Title'], file_data['Year'],
        file_data['Released'], file_data['Genre'], file_data['imdbRating'],
        file_data['Runtime'], file_data['Director'], file_data['Actors'],
        file_data['Plot'], file_data['Poster']))
    conn.commit()


def get_movie_name(filename):
    # TODO if filename doesnt get any results on imdb, maybe we can use the
    # folder name
    old_filename = filename

    # make sure reject words dont have a char which is special in regexes, or
    # else it shud be properly escaped
    # Remove everything after a reject word
    reject_words = ['dvd', 'xvid', 'brrip', 'r5', 'unrated', '720p', 'x264',
                    'klaxxon', 'axxo', 'br_300', '300mb', 'cd1', 'cd2']
    reject_words_strict = ['eng', 'scr', 'dual']  # UNUSED

    # dont process this file if a panic word is found
    panic_words = ['sample']

    #prepare: remove ext, make lower
    filename = ".".join(filename.split('.')[:-1])
    filename = filename.lower()

    #0 panic words
    for word in panic_words:
        if (filename.find(word) != -1):
            return ''

    #1 remove everythin in brackets
    brackets = [('\(','\)'), ('\[', '\]'), ('\{', '\}')]
    for b in brackets:
        filename = re.sub(b[0] + '.*?' + b[1], ' ', filename)

    #2 remove year and stuff following it
    filename = re.sub('\d\d\d\d.*', ' ', filename)

    #3 reject_words
    for word in reject_words:
        filename = re.sub(word + '.*', ' ', filename)

    #cleanup
    filename = re.sub('\s+', ' ', re.sub(
        '[\._\-\(\)\[\]\{\}]', ' ', filename).strip())

    print old_filename, filename
    return filename


def get_imdb_data(moviename):
    if (moviename == ' ' or moviename == ''):
        return None

    try:
        res = json.load(urllib2.urlopen(api_url + urllib2.quote(moviename) +
            api_extra_opts))
    except urllib2.URLError, e:
        return None

    if (res['Response'] == 'True'):
        return res
    else:
        return None


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


#CLASSES#
class DBbuilderThread(threading.Thread):
    def __init__(self, parent, files, mdb_dir):
        threading.Thread.__init__(self)
        self.parent = parent
        self.files = files
        self.mdb_dir = mdb_dir

    def run(self):
        """Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        """
        print 'dbbuilder running'
        self.process_files()
        print 'dbbuilder exiting'

    def signal_gui(self, filename):
        evt = wx_signal.FileDoneEvent(wx_signal.myEVT_FILE_DONE, -1, filename)
        wx.PostEvent(self.parent, evt)

    def process_file(self, filename, conn, cur):
        file_data = get_imdb_data(get_movie_name(filename))
        if (file_data is None):
            print "None data from imdb for", filename
            return

        for item in file_data:
            if file_data[item] == 'N/A':
                file_data[item] = None

        if (file_data is not None):
            # Add to db, save img, send signal
            add_to_db(filename, file_data, conn, cur)
            if file_data['Poster'] is not None:
                # save image
                img_url = file_data['Poster'][:-7] + img_size + '.jpg'
                img_file = os.path.join(self.mdb_dir, images_folder,
                                        filename + '.jpg')
                img_fh = open(img_file, 'wb')
                img_fh.write(urllib2.urlopen(img_url).read())
                img_fh.close()
            self.signal_gui(filename)
            print 'file processed'

    def process_files(self):
        # set proxies
        if (http_proxy is not None):
            os.environ['http_proxy'] = http_proxy
        if (https_proxy is not None):
            os.environ['https_proxy'] = https_proxy

        conn = sqlite3.connect(os.path.join(self.mdb_dir, db_name))
        cur = conn.cursor()

        try:
            for filename in self.files:
                self.process_file(filename, conn, cur)
        except Exception, e:
            zenity_error(str(e))
            raise
