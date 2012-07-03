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


def post_process():
    type_conv()
    handle_proxy()


def handle_proxy():
    if (config['http_proxy'] != 'None' and len(config['http_proxy']) > 0):
        os.environ['http_proxy'] = config['http_proxy']


def type_conv():
    if (config['debug'] == 'True'):
        config['debug'] = True
    else:
        config['debug'] = False

    config['upd_freq'] = int(config['upd_freq'])
    config['update_last_checked'] = int(config['update_last_checked'])


#Non configurable stuff
version = '0.1'

out_dir = '.mdb'
mdb_dir = os.path.join(os.path.expanduser('~'), out_dir)
db_name = 'mdbdata.sqlite'
images_folder = 'images'
config_file_path = os.path.join(mdb_dir, '.config')

api_url = 'http://www.imdbapi.com'
api_movie_param = 't'
api_extra_opts = {}  # '&plot=full'

movie_formats = ['avi', 'mkv', 'mp4', 'm4v', 'rmvb']

img_size = '100'

imdb_icon = os.path.join(module_path(), 'resources/images/imdb-logo.png')

platform = get_platform()

update_url = 'http://legaloslotr.github.com/mdb/update.html'

abt_dlg_content = '''
<body bgcolor="#f1f1f1">
<center>
<h2>MDB - MovieDirBrowser</h2>
v{0}<br>
<a href="http://legaloslotr.github.com/mdb">
http://legaloslotr.github.com/mdb</a><br>
Data collected from <a href="http://imdb.com">IMDB</a>
</center></body>
'''.format(version)

cant_connect_content = {
    'title': 'Connection Error',
    'body': "Unable to connect to the internet.\
            \nPlease check your internet connection.",
}

#Configurable stuff
defaults = {
        'http_proxy': 'None',
        'debug': 'False',
        'update_last_checked': '0',
        'upd_freq': '7',  # days
}

prefs_item_map = [
        ('debug', 'bool', 'Debug Mode'),
        ('http_proxy', 'str', 'Http Proxy'),
        ('upd_freq', 'str', 'Update Frequency(days)')
]

config = ConfigObj(defaults)
config.merge(ConfigObj(config_file_path))
config.filename = config_file_path

# FIXME dont do this here
if (not os.path.exists(mdb_dir)):
    os.mkdir(mdb_dir)

config.write()
post_process()
