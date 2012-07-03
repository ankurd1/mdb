#!/usr/bin/python

import os
from subprocess import call
import sys
import sqlite3
import wx_signal
import wx
import re
import threading
import config
import requests


#HELPER FUNCTIONS#
def zenity_error(msg):
    sys.stderr.write(msg + '\n')
    if (config.config['debug']):
        try:
            call(['zenity', '--error', '--text', msg])
        except OSError, e:
            pass
            # zenity not available


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
            poster TEXT,
            imdbID TEXT
            )''')
    cur.execute('CREATE UNIQUE INDEX filename_index ON movies (filename)')
    conn.commit()


def add_to_db(filename, file_data, conn, cur):
    if (is_in_db(conn, cur, filename)):
        return

    cur.execute('INSERT INTO movies VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', (
        filename, file_data['Title'], file_data['Year'],
        file_data['Released'], file_data['Genre'], file_data['imdbRating'],
        file_data['Runtime'], file_data['Director'], file_data['Actors'],
        file_data['Plot'], file_data['Poster'], file_data['imdbID']))
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
    brackets = [('\(', '\)'), ('\[', '\]'), ('\{', '\}')]
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
        return None, True

    params = {
            config.api_movie_param: moviename,
            }
    params.update(config.api_extra_opts)

    try:
        response = requests.get(config.api_url, params=params)
    except requests.RequestException, e:
        print "DBbuilder: RequestException", e
        return None, False

    if (not response.ok):
        # Should we stop further processing here?
        print "Some error with the api!"
        return None, True

    if (response.json['Response'] == 'True'):
        return response.json
    else:
        return None, True


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
    def __init__(self, parent, files):
        threading.Thread.__init__(self)
        self.parent = parent
        self.files = files
        self.exit_now = False

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
        file_data, process_further = get_imdb_data(get_movie_name(filename))
        if (not process_further):
            return False

        if (file_data is None):
            print "None data from imdb for", filename
            return True

        for item in file_data:
            if file_data[item] == 'N/A':
                file_data[item] = None

        if (file_data is not None):
            # Add to db, save img, send signal
            add_to_db(filename, file_data, conn, cur)
            if file_data['Poster'] is not None:
                # save image
                img_url = file_data['Poster'][:-7] + config.img_size + '.jpg'
                img_file = os.path.join(config.mdb_dir, config.images_folder,
                                        filename + '.jpg')
                img_fh = open(img_file, 'wb')
                img_fh.write(requests.get(img_url).content)
                img_fh.close()
            self.signal_gui(filename)
            print 'file processed'
        return True

    def process_files(self):
        conn = sqlite3.connect(os.path.join(config.mdb_dir, config.db_name))
        cur = conn.cursor()

        try:
            for filename in self.files:
                if (self.exit_now):
                    return
                process_further = self.process_file(filename, conn, cur)
                if (not process_further):
                    evt = wx_signal.ShowMsgEvent(wx_signal.myEVT_SHOW_MSG, -1,
                            config.cant_connect_content)
                    wx.PostEvent(self.parent, evt)
                    return
        except Exception, e:
            zenity_error(str(e))
            raise
