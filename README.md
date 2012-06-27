# MDB (MovieDirBrowser)

MDB is a cool way to visualize your movie collection and decide which movie to
watch next! Run MDB on a folder or a set of files/folders and it downloads imdb 
data for all movie files found and shows it in a nice GUI.

You can then sort the movies by title, rating, runtime, releaseYear or Genre.
All this data is cached on your computer, so we don't need to hit imdb
the next time!

MDB runs on Windows and Linux.

## Installation

### Linux
Download the zip from [here](http://example.com) and extract it somewhere.

If you want to enable right-click shortcuts for gnome, copy the mdb-launcher.py
file to ~/.gnome2/nautilus-scripts.
```
cp mdb-launcher.py ~/.gnome2/nautilus-scripts/mdb && chmod u+x ~/.gnome2/nautilus-scripts/mdb
```

### Windows
Download the zip from [here](http://example.com) and extract it somewhere.

If you want to enable right-click shortcuts, double-click reg-gen.exe to
generate a shortcuts.reg file; then double click the generated shortcuts.reg to
add it to your registry.

## Usage
* Right-click anywhere in a movie folder and select MDB! (On linux, you would
  have to select scripts->MDB in the right-click menu).
* You can also right-click a file/folder and select MDB. On linux, you can even
  select multiple files/folders before right-clicking.
* Or you could just run gui.py OR gui.exe to launch the program. You can also
  provide arguments to the program, otherwise the current working dir would be
  scanned for movie files.
* Once the program is running, you can sort by clicking on a column name OR you
  can switch to another folder by selecting File->Open (Ctrl+O).

## Coming soon
* Ability to download subtitles.
* Better installation methods.
* Configuration options.
* Ability to search for title/director/actor/genre.
