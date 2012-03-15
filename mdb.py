#!/usr/bin/python

import re


def get_movie_name(filename):
    # 1. Find a year, reject everything after it, clean up
    # 2. Find a reject word(like Dvd, brrip, xvid), reject everything
    # after it, clean up
    # 3. Split by some token, try to remove the last words and do a
    # search #NOT_IMPLEMENTED
    reject_words = ['dvd', 'xvid', 'brrip', 'r5', 'unrated', '720p',
            'x264', 'klaxxon', 'axxo']
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
