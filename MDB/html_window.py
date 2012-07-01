import wx.html
from lib import get_platform
from subprocess import call

class ClickableHtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, *args, **kwargs):
        wx.html.HtmlWindow.__init__(self, parent, *args, **kwargs)

    def OnLinkClicked(self, linkinfo):
        platform = get_platform()
        if (platform == 'linux'):
            call(['xdg-open', linkinfo.GetHref()])
        elif (platform == 'windows'):
            try:
                from os import startfile
            except ImportError, e:
                return
            startfile(linkinfo.GetHref())
