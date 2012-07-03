#!/usr/bin/python

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

import sys
import os
import glob
import shutil
from subprocess import call


# FIXME version is also defined in config.py
VERSION = '0.1'


# FIXME this code is also in config.py!
def get_platform():
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('linux'):
        return 'linux'
    else:
        return None


def is_yes(quest):
    print quest
    ans = sys.stdin.readline()
    if (ans.lower().startswith('y')):
        return True
    else:
        return False


setup_options = {
        'name': 'MDB',
        'version': VERSION,
        'description': 'Browse imdb data for a folder full of movies!',
        'author': 'Ankur Dahiya',
        'author_email': 'legalos.lotr@gmail.com',
        'packages': ['MDB'],
        'url': 'http://legaloslotr.github.com/mdb',
        'package_data': {'MDB': ['resources/images/*']},
        'install_requires': ['configobj', 'requests']
        }

win_options = {
        'windows': [{'script':'bin/MDB'}],
        'options': {'py2exe': {'bundle_files': 2}},
        }

lin_options = {
        'scripts': ['bin/MDB'],
        }

lin_nautilus_script_out = os.path.expanduser('~/.gnome2/nautilus-scripts/MDB')
lin_nautilus_script_in = 'setup/linux/nautilus-script.py'

if __name__ == '__main__':
    action = sys.argv[1]

    if (get_platform() == 'windows'):
        if (action == 'py2exe'):
            import py2exe

            # setup dlls
            dll_dir = 'dll'
            if (os.path.exists(dll_dir)):
                data_files = []
                for f in os.listdir(dll_dir):
                    f_abs = os.path.abspath(os.path.join(dll_dir, f))
                    if (os.path.isdir(f_abs)):
                        data_files.append((f, glob.glob(os.path.join(f_abs, '*'))))
                        sys.path.append(f_abs)
                    else:
                        data_files.append(('', [f_abs]))

                sys.path.append(dll_dir)
                setup_options['data_files'] = data_files

            setup_options.update(win_options)
            setup(**setup_options)

            # py2exe ignores package_data, lets fix that
            # FIXME, this is hacky
            # copy all dirs from each package which are not modules
            print 'Copying package data...'
            for item in setup_options['packages']:
                for f in os.listdir(item):
                    if (os.path.isdir(item + '\\' + f)):
                        shutil.copytree(item + '\\' + f, 'dist\\' + f)

            if (is_yes("Do you want to build the installer? (y/n)")):
                iss_file = 'setup/windows/MDB.iss'
                call(['Compil32.exe', '/cc', iss_file])
        else:
            setup_options.update(win_options)
            setup(**setup_options)

    elif (get_platform() == 'linux'):
        if (action == 'install'):
            # check for wxpython
            try: import wx
            except ImportError, e:
                print "wxPython was not found on your system. Please install it " +\
                        "before proceeding further.\nOn debian based system, " +\
                        "this can be done by running:\n" +\
                        "sudo apt-get install python-wxgtk2.8"
                sys.exit(-1)

        # TODO Also install a .desktop file and an uninstaler.
        setup_options.update(lin_options)
        setup(**setup_options)

        if (action == 'install'):
            if (is_yes("Do you want to install right-click shortcuts for " +\
                    "nautilus/gnome? (y/n)")):
                # copy nautilus-shortcuts.py to nautilus scripts
                try: os.unlink(lin_nautilus_script_out)
                except: pass
                shutil.copy(lin_nautilus_script_in, lin_nautilus_script_out)
                os.chmod(lin_nautilus_script_out, 0777)
                print "Shortcuts installed successfully."
    else:
        print "Platform/action not supported."
