from kivymd.dialog import MDDialog
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime


def show_dialog(title, text, ok_proc, inform=False):
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

    if inform:
        dialog.add_action_button(app.translation._('ОК'),
                                 action=lambda *x: dialog.dismiss())
    else:
        dialog.add_action_button(app.translation._('ОК'),
                                 action=lambda *x: ok_proc(dialog))
        dialog.add_action_button(app.translation._('Отмена'),
                                 action=lambda *x: dialog.dismiss())
    dialog.open()


# конвертация даты
def get_date(str):
    # ищу разделитель между цифрами, менялся с . на -
    if str.find('-') >= 0:
        d = '-'
    else:
        d = '.'
    # что сначала - год?
    if str.find(d) == 4:
        fmt = '%Y' + d + '%m' + d + '%d %H:%M:%S'
    else:
        fmt = '%d' + d + '%m' + d + '%Y %H:%M:%S'
    if len(str) > 10:
        return datetime.strptime(str, fmt)
    else:
        return datetime.strptime(str, fmt[:8])


urgency_dict = {'1': 'Очень важно', '2': 'Важно', '3': 'Нормальная', '4': 'Не важно', '6': 'Срочно'}
urgency_color = {'1': '#FFA500', '2': '#FFC500', '3': '#00FF00', '4': '#0000FF', '6': '#FF0000'}