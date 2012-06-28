#!/usr/bin/python

import distutils.command.install
from distutils.core import setup
import sys
import os
import shutil

try:
    import py2exe
except ImportError, e:
    pass


def get_platform():
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('linux'):
        return 'linux'
    else:
        return None

setup_options = {
        'name' : 'MDB',
        'version' : '0.8a',
        'description' : 'Browse imdb data for a folder full of movies!',
        'author' : 'Ankur Dahiya',
        'author_email' : 'legalos.lotr@gmail.com',
        'packages' : ['MDB'],
        'url' : 'http://legaloslotr.github.com/mdb',
        }

win_options = {
        'windows' : [{'script':'MDB/gui.py'}],
        'console' : [{'script':'tools/reg-gen.py'}],
        'options' : {'py2exe': {'bundle_files': 2}},
        }

lin_options = {
        'scripts' : ['setup/linux/MDB'],
        }

lin_nautilus_script_out = os.path.expanduser('~/.gnome2/nautilus-scripts/MDB')
lin_nautilus_script_in = 'setup/linux/nautilus-script.py'

if __name__ == '__main__':
    platform = get_platform()
    if (platform == 'windows'):
        setup_options.update(win_options)
        setup(**setup_options)
        # TODO create the installer
    elif (platform == 'linux'):
        setup_options.update(lin_options)
        setup(**setup_options)

        # copy nautilus-shortcuts.py to nautilus scripts
        shutil.copy(lin_nautilus_script_in, lin_nautilus_script_out)
        os.chmod(lin_nautilus_script_out, 0777)
    else:
        print "Platform not supported."
