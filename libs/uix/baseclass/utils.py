from kivymd.dialog import MDDialog
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.app import App


def confirm_dialog(title, text, ok_proc):
    app = App.get_running_app()
    content = Label()
    content.text = text
    content.color = [0, 0, 0, 1]
    content.size_hint = (1, None)
    content.height = 50

    dialog = MDDialog(title=title,
                      content=content,
                      size_hint=(.8, None),
                      height=dp(200),
                      auto_dismiss=False)

    dialog.add_action_button(app.translation._('ОК'),
                                  action=lambda *x: ok_proc(dialog))
    dialog.add_action_button(app.translation._('Отмена'),
                                  action=lambda *x: dialog.dismiss())
    dialog.open()

