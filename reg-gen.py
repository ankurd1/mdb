#!/usr/bin/python

import os

if __name__ == '__main__':
    out_file_path = 'shortcuts.reg'
    in_file_path = 'shortcuts-reg.template'

    new_path = os.path.join(os.getcwd(), 'gui.exe')
    new_path = new_path.replace('\\', '\\\\')
    reg_text = open(in_file_path).read()
    reg_text = reg_text.replace('PATH_TO_GUI', new_path)

    out_file = open(out_file_path, 'w')
    out_file.write(reg_text)
    out_file.close()
