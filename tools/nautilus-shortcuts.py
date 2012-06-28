#!/usr/bin/python

import os

out_file_path = os.path.expanduser('~/.gnome2/nautilus-scripts/MDB')
in_file_path = '../resources/templates/nautilus-script.template'

if __name__ == '__main__':
    launcher_script_text = open(in_file_path).read()
    launcher_script_text = launcher_script_text.replace('MDB_PATH',
            os.path.abspath('../MDB'))

    out_file = open(out_file_path, 'w')
    out_file.write(launcher_script_text)
    out_file.close()

    os.chmod(out_file_path, 0744)
