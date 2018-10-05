from kivy.uix.screenmanager import Screen

class SettingsForm(Screen):

    def GetSettings(self):
        try:
            self.ip.text = self.manager.app.config.get('General', 'IP')
            self.user.text = self.manager.app.config.get('General', 'user')
            self.password.text = self.manager.app.config.get('General', 'password')
            self.sms.text = self.manager.app.config.get('General', 'sms')
        except:
            pass

    def SetSetting(self):
        self.manager.app.config.set('General', 'IP', self.ip.text)
        self.manager.app.config.set('General', 'user', self.user.text)
        self.manager.app.config.set('General', 'password', self.password.text)
        self.manager.app.config.set('General', 'sms', self.sms.text)
        self.manager.app.config.write()
        self.manager.app.set_value_from_config()

    def on_enter(self, *args):
        self.GetSettings()

    def on_leave(self, *args):
        self.SetSetting()