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
import Queue
import time


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

    return filename


def get_imdb_data(filename, queue):
    moviename = get_movie_name(filename)
    if (moviename == ' ' or moviename == ''):
        queue.put((None, filename, False))
        print "thread done", filename
        return

    params = {config.api_movie_param: moviename}
    params.update(config.api_extra_opts)

    try:
        response = requests.get(config.api_url, params=params)
    except requests.RequestException, e:
        queue.put((None, filename, True))
        print "thread done", filename
        return

    if (not response.ok):
        # Should we stop further processing here?
        print "Some error with the api!"
        queue.put((None, filename, False))
        print "thread done", filename
        return

    if (response.json['Response'] == 'True'):
        for item in response.json:
            if response.json[item] == 'N/A':
                response.json[item] = None

        process_img(response.json['Poster'], filename)
        queue.put((response.json, filename, False))
        #print "thread done", filename
        return
    else:
        print "none data for", filename
        queue.put((None, filename, False))
        print "thread done", filename
        return


def process_img(poster, filename):
    if (poster is None):
        return
    img_url = poster[:-7] + config.img_size + '.jpg'
    img_file = os.path.join(config.mdb_dir, config.images_folder,
                            filename + '.jpg')
    img_fh = open(img_file, 'wb')
    try:
        img_fh.write(requests.get(img_url).content)
    except requests.RequestException, e:
        # do nothing?
        pass
    img_fh.close()


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


def signal_gui(parent, filename):
    evt = wx_signal.FileDoneEvent(wx_signal.myEVT_FILE_DONE, -1, filename)
    wx.PostEvent(parent, evt)


def process_files(files, gui_ready, parent, threadpool, exit_now):
    conn = sqlite3.connect(os.path.join(config.mdb_dir, config.db_name))
    cur = conn.cursor()

    file_data_queue = Queue.Queue()
    threadpool.map_async(lambda fil, queue=file_data_queue:
            get_imdb_data(fil, queue), files)

    for t in threading.enumerate():
        print t.name, t.daemon

    for i in range(len(files)):
        if (gui_ready.wait()):
            gui_ready.clear()
            if (exit_now.is_set()):
                print "dbbuilder recd exit_now, exiting"
                return

            imdb_data, filename, conn_err = file_data_queue.get()
            print "dbbuilder recd", filename

            if (conn_err):
                evt = wx_signal.ShowMsgEvent(wx_signal.myEVT_SHOW_MSG, -1,
                        config.cant_connect_content)
                wx.PostEvent(parent, evt)
                return

            if (imdb_data is not None):
                add_to_db(filename, imdb_data, conn, cur)
                signal_gui(parent, filename)
                print "processed", filename
            else:
                gui_ready.set()


class DBbuilderThread(threading.Thread):
    def __init__(self, parent, files, threadpool):
        threading.Thread.__init__(self)
        self.parent = parent
        self.files = files
        self.gui_ready = threading.Event()
        self.gui_ready.set()
        self.exit_now = threading.Event()
        self.exit_now.clear()
        self.threadpool = threadpool

    def run(self):
        """Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        """
        print 'dbbuilder running'
        start = time.time()
        process_files(self.files, self.gui_ready, self.parent, self.threadpool,
                self.exit_now)
        print 'dbbuilder exiting'
        print '{0} files processed in {1}s'.format(len(self.files),
                time.time() - start)
