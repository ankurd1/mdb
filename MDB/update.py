import threading
import time
import requests
import config
from dialogs import HtmlDialog


class UpdateThread(threading.Thread):
    def __init__(self, parent, force=False):
        threading.Thread.__init__(self)
        self.parent = parent
        self.force = force
        self.exit_now = False

    def run(self):
        """Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        """
        print 'update thread running'
        self.check_for_updates()
        print 'update thread exiting'

    def show_upd_dialog(self, data):
        abt_dlg = HtmlDialog(None, content=data['dlg_content'])
        abt_dlg.ShowModal()
        abt_dlg.Destroy()

    def check_for_updates(self, force=False):
        time_to_cmp = (config.config['update_last_checked'] +
            (config.config['upd_freq'] * 24 * 3600))
        if (force or (int(time.time()) > time_to_cmp)):
            try:
                upd_data = requests.get(config.update_url)
            except requests.RequestException, e:
                print "RequestException", e
                # FIXME Back off for some time  or check after 7 days?
                return

            if (upd_data.ok and 'version' in upd_data.json):
                # FIXME make sure versions can be compared as strings!
                if (upd_data.json['version'] > config.version):
                    print "valid update found"
                    self.show_upd_dialog(upd_data.json)

            config.config['update_last_checked'] = int(time.time())
            config.config.write()
            config.post_process()
