import wx.html
from subprocess import call
import config


class ClickableHtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, *args, **kwargs):
        wx.html.HtmlWindow.__init__(self, parent, *args, **kwargs)

    def OnLinkClicked(self, linkinfo):
        if (config.platform == 'linux'):
            call(['xdg-open', linkinfo.GetHref()])
        elif (config.platform == 'windows'):
            try:
                from os import startfile
            except ImportError, e:
                return
            startfile(linkinfo.GetHref())

    def attach_to_frame(self, frame, sb_slot):
        self.SetRelatedFrame(frame, "")
        self.SetRelatedStatusBar(sb_slot)
