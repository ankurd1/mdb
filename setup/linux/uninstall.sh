#!/bin/bash
sudo updatedb
locate MDB | grep -v home | grep /usr | while read line; do sudo rm -Rf $line; done
sudo updatedb
rm ~/.gnome2/nautilus-scripts/MDB
