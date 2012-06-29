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
        'windows' : [{'script':'bin/MDB'}],
        'options' : {'py2exe': {'bundle_files': 2}},
        }

lin_options = {
        'scripts' : ['bin/MDB'],
        }

lin_nautilus_script_out = os.path.expanduser('~/.gnome2/nautilus-scripts/MDB')
lin_nautilus_script_in = 'setup/linux/nautilus-script.py'

if __name__ == '__main__':
    platform = get_platform()
    action = sys.argv[1]

    if (platform == 'windows' and action == 'py2exe'):
        setup_options.update(win_options)
        setup(**setup_options)
        # TODO create the installer
    elif (platform == 'linux'):
        # TODO Also install a .desktop file and an uninstaler.
        setup_options.update(lin_options)
        setup(**setup_options)

        if (action == 'install'):
            print "Do you want to install right-click shortcuts for nautilus/gnome?"
            ans = sys.stdin.readline()
            if ans.lower().startswith('y'):
                # copy nautilus-shortcuts.py to nautilus scripts
                shutil.copy(lin_nautilus_script_in, lin_nautilus_script_out)
                os.chmod(lin_nautilus_script_out, 0777)
                print "Shortcuts installed successfully."
    else:
        print "Platform/action not supported."
