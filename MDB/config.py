from configobj import ConfigObj
import os
import sys


#helper methods
def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")


def module_path():
    encoding = sys.getfilesystemencoding()
    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, encoding))
    return os.path.dirname(unicode(__file__, encoding))


def get_platform():
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('linux'):
        return 'linux'
    else:
        return None

#Non configurable stuff
version = '0.1'
out_dir = '.mdb'
mdb_dir = os.path.join(os.path.expanduser('~'), out_dir)
config_file_path = os.path.join(mdb_dir, '.config')
api_url = 'http://www.imdbapi.com/?t='
api_extra_opts = ''  # '&plot=full'
db_name = 'mdbdata.sqlite'
images_folder = 'images'
movie_formats = ['avi', 'mkv', 'mp4', 'm4v', 'rmvb']
img_size = '100'
imdb_icon = os.path.join(module_path(), 'resources/images/imdb-logo.png')
platform = get_platform()

#Configurable stuff
defaults = {
        'http_proxy': 'None',
        'debug': 'False'
}

config = ConfigObj(defaults)
config.merge(ConfigObj(config_file_path))

#handle proxy
if (config['http_proxy'] != 'None'):
    os.environ['http_proxy'] = config['http_proxy']

#type conversion
config['debug'] = bool(config['debug'])

if (config['debug']):
    print config
