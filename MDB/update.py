import threading
import time
import requests
import config
import wx_signal
import wx


class UpdateThread(threading.Thread):
    def __init__(self, parent, force=False):
        threading.Thread.__init__(self)
        self.parent = parent
        self.force = force

    def run(self):
        """Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        """
        print 'update thread running'
        self.check_for_updates()
        print 'update thread exiting'

    def show_upd_dialog(self, data):
        content = {
                'title': 'Updates',
                'body': data['dlg_content']
        }
        evt = wx_signal.ShowMsgEvent(wx_signal.myEVT_SHOW_MSG, -1,
                content, True)
        wx.PostEvent(self.parent, evt)

    def check_for_updates(self):
        time_to_cmp = (config.config['update_last_checked'] +
            (config.config['upd_freq'] * 24 * 3600))
        if (self.force or (int(time.time()) > time_to_cmp)):
            try:
                upd_data = requests.get(config.update_url)
            except requests.RequestException, e:
                print "RequestException", e
                if (self.force):
                    evt = wx_signal.ShowMsgEvent(wx_signal.myEVT_SHOW_MSG, -1,
                            config.cant_connect_content)
                    wx.PostEvent(self.parent, evt)
                # FIXME Back off for some time  or check after 7 days?
                return

            if (upd_data.ok and 'version' in upd_data.json and\
                    upd_data.json['version'] > config.version):
                # FIXME make sure versions can be compared as strings!
                print "valid update found"
                self.show_upd_dialog(upd_data.json)
            else:
                print 'no updates'
                # report no updates
                if (self.force):
                    evt = wx_signal.ShowMsgEvent(wx_signal.myEVT_SHOW_MSG, -1,
                            config.no_updates_content)
                    wx.PostEvent(self.parent, evt)

            config.config['update_last_checked'] = int(time.time())
            config.config.write()
            config.post_process()
        else:
            print "nothing to do here"
