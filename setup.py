#!/usr/bin/python

import distutils.command.install
from distutils.core import setup
import sys
import os
import glob
import shutil
from subprocess import call
from MDB.lib import get_platform


def is_yes(quest):
    print quest
    ans = sys.stdin.readline()
    if (ans.lower().startswith('y')):
        return True
    else:
        return False


setup_options = {
        'name' : 'MDB',
        'version' : '0.8a',
        'description' : 'Browse imdb data for a folder full of movies!',
        'author' : 'Ankur Dahiya',
        'author_email' : 'legalos.lotr@gmail.com',
        'packages' : ['MDB'],
        'url' : 'http://legaloslotr.github.com/mdb',
        'package_data' : {'MDB' : ['resources/images/*']}
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
                if (os.path.isdir(item+'\\'+f)):
                    shutil.copytree(item+'\\'+f, 'dist\\'+f)

        if (is_yes("Do you want to build the installer? (y/n)")):
            iss_file = 'setup/windows/MDB.iss'
            call(['Compil32.exe', '/cc', iss_file])

    elif (platform == 'linux'):
        # TODO Also install a .desktop file and an uninstaler.
        setup_options.update(lin_options)
        setup(**setup_options)

        if (action == 'install'):
            if (is_yes("Do you want to install right-click shortcuts for " +\
                    "nautilus/gnome? (y/n)")):
                # copy nautilus-shortcuts.py to nautilus scripts
                shutil.copy(lin_nautilus_script_in, lin_nautilus_script_out)
                os.chmod(lin_nautilus_script_out, 0777)
                print "Shortcuts installed successfully."
    else:
        print "Platform/action not supported."
