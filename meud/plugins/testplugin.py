import wx

from _plugin import Plugin

class TestPlugin(Plugin):
    name = "Test"
    
    def get_actions(self, item):
        return ["Who am I?"]
    
    def do_action(self, item, workspace, action):
        if action == "Who am I?":
            if item.precessor:
                precessor_type = item.precessor.type
            else:
                precessor_type = None
            msg = u"You are {0}\n\
                   Path: {1}\n\
                   Parent: {2}\n\
                   Dir: {3}\n\
                   Type: {4}\n\
                   Precessor type: {5}".format(item.name, item.path, item.parent, item.dir, item.type,
                                               precessor_type)
            dlg = wx.MessageDialog(None, msg,
                               "Test",
                               wx.OK | wx.ICON_INFORMATION
                               )
            dlg.ShowModal()
            dlg.Destroy()