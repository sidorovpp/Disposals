from kivy.uix.screenmanager import Screen
from kivy.app import App

class SettingsForm(Screen):

    def GetSettings(self):
        try:
            self.ids.ip.text = self.manager.app.config.get('General', 'IP')
            self.ids.user.text = self.manager.app.config.get('General', 'user')
            self.ids.password.text = self.manager.app.config.get('General', 'password')
        except:
            pass

    def SetSetting(self):
        self.manager.app.config.set('General', 'IP', self.ids.ip.text)
        self.manager.app.config.set('General', 'user', self.ids.user.text)
        self.manager.app.config.set('General', 'password', self.ids.password.text)
        self.manager.app.config.write()
        self.manager.app.set_value_from_config()

    def on_enter(self, *args):
        self.GetSettings()

    def on_leave(self, *args):
        self.SetSetting()