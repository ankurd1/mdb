import wx.html
import wx
from subprocess import call
import config


class ClickableHtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, *args, **kwargs):
        wx.html.HtmlWindow.__init__(self, parent, *args, **kwargs)

    def OnCellClicked(self, cell, x, y, evt):
        print "oncellclicked"
        selection = self.SelectionToText()
        link = cell.GetLink()
        button = evt.GetButton()

        if (button == 1 and link is not None):
            # left click on hyperlink
            if (config.platform == 'linux'):
                call(['xdg-open', cell.GetLink().GetHref()])
            elif (config.platform == 'windows'):
                try:
                    from os import startfile
                except ImportError, e:
                    return
                startfile(cell.GetLink().GetHref())
        elif (button == 3 and (len(selection) > 0 or link is not None)):
            menu = wx.Menu()
            if (len(selection) > 0):
                copy = menu.Append(wx.ID_ANY, "Copy")
                self.Bind(wx.EVT_MENU, self.on_copy, copy)
            if (link is not None):
                copy_link = menu.Append(wx.ID_ANY, "Copy Link")
                self.Bind(wx.EVT_MENU,
                        lambda evt, link=link : self.on_copy_link(evt, link),
                        copy_link)

            self.PopupMenu(menu, evt.GetPosition())
            menu.Destroy()

    def on_copy(self, evt):
        self.add_to_clipboard(self.SelectionToText())

    def on_copy_link(self, evt, link):
        self.add_to_clipboard(link.GetHref())

    def add_to_clipboard(self, txt):
        wx.TheClipboard.UsePrimarySelection(False)
        if wx.TheClipboard.Open():
            do = wx.TextDataObject()
            do.SetText(txt)

            wx.TheClipboard.SetData(do)
            wx.TheClipboard.Close()
            wx.TheClipboard.Flush()

            print "Added to clipboard", txt
        else:
            print "Unable to open clipboard"

    def attach_to_frame(self, frame, sb_slot):
        self.SetRelatedFrame(frame, "")
        self.SetRelatedStatusBar(sb_slot)
