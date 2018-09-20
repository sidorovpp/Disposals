from kivy.uix.screenmanager import Screen
from kivy.app import App

class SettingsForm(Screen):

    def GetSettings(self):
        app = App.get_running_app()
        try:
            self.ids.ip.text = app.config.get('General', 'IP')
            self.ids.user.text = app.config.get('General', 'user')
            self.ids.password.text = app.config.get('General', 'password')
        except:
            pass

    def SetSetting(self):
        app = App.get_running_app()
        app.config.set('General', 'IP', self.ids.ip.text)
        app.config.set('General', 'user', self.ids.user.text)
        app.config.set('General', 'password', self.ids.password.text)
        app.config.write()
        app.set_value_from_config()

    def on_enter(self, *args):
        self.GetSettings()

    def on_leave(self, *args):
        self.SetSetting()