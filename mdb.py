#!/usr/bin/python

import re
import urllib2
import simplejson
import os
from subprocess import call

api_url = 'http://www.imdbapi.com/?t='
out_file = '.mdbdata'
movie_formats = ['avi', 'mkv']


def get_movie_name(filename):
    # 1. Find a year, reject everything after it, clean up
    # 2. Find a reject word(like Dvd, brrip, xvid), reject everything
    # after it, clean up
    # 3. Split by some token, try to remove the last words and do a
    # search #NOT_IMPLEMENTED
    reject_words = ['dvd', 'xvid', 'brrip', 'r5', 'unrated', '720p',
            'x264', 'klaxxon', 'axxo', 'sample']
    reject_words_strict = ['eng', 'scr', 'dual']  # UNUSED

    #prepare: remove ext, make lower
    if (filename[-4] == '.'):
        filename = filename[:-4]

    filename = filename.lower()

    #1
    year_split = re.split('\d\d\d\d', filename)
    if (len(year_split) > 1):
        filename = year_split[0]

    #2
    for word in reject_words:
        if (filename.find(word) != -1):
            filename = filename[:filename.find(word)]

    #cleanup
    filename = re.sub('\s+', ' ',
            re.sub('[\._\-\[\(\]\)]', ' ', filename).strip())

    return filename


def get_imdb_data(moviename):
    res = simplejson.load(urllib2.urlopen(api_url + urllib2.quote(moviename)))
    if (res['Response'] == 'True'):
        return res
    else:
        return None


def display_out_file():
    if (os.path.exists(out_file)):
        call(['gvim', out_file])


def format_file_data(file_data, filename):
    for i in file_data:
        file_data[i] = file_data[i].encode('ascii','ignore')

    res = 'File: {0}\nTitle: {1}\nYear: {2}\nGenre: {3}\nRating: {4}\n\
Runtime: {5}\nDirector: {6}\nActors: {7}\n\
Plot: {8}\n'.format(filename, file_data['Title'], file_data['Year'],
        file_data['Genre'], file_data['Rating'], file_data['Runtime'],
        file_data['Director'], file_data['Actors'], file_data['Plot'])

    return res


def process_file(filename, out):
    movie = get_movie_name(filename)
    file_data = get_imdb_data(get_movie_name(movie))
    if (file_data is not None):
        out.write(format_file_data(file_data, filename))
        out.write('\n')


def main():
    target_dir = os.getcwd()

    if (os.path.exists(out_file)):
        display_out_file()
    else:
        with open(out_file, 'w') as out:
            for filename in os.listdir(target_dir):
                if (os.path.isdir(filename)):
                    for filename2 in os.listdir(filename):
                        if (filename2[-3:] in movie_formats):
                            process_file(filename2, out)

                if (filename[-3:] in movie_formats):
                    process_file(filename, out)

        display_out_file()


if __name__ == '__main__':
    main()
