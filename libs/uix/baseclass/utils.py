from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.app import App
from datetime import datetime
import re
from kivy.utils import get_hex_from_color

class CustomDialog():
    dialog = None
    ok_proc = None

    def dialog_dismiss(self, inst):
        self.dialog.dismiss()
        self.dialog = None

    def execute_proc(self, inst):
        self.ok_proc(self.dialog)
        self.dialog = None

    def show_dialog(self, title, text, ok_proc, inform=False):
        self.ok_proc = ok_proc
        app = App.get_running_app()
        if not self.dialog:
            if inform:
                self.dialog = MDDialog(
                    text=text,
                    buttons=[
                        MDFlatButton(
                            text=app.translation._('ОК'), text_color=app.theme_cls.primary_color, on_release = self.dialog_dismiss
                        ),
                    ],
                )
            else:
                self.dialog = MDDialog(
                    text=text,
                    buttons=[
                        MDFlatButton(
                            text=app.translation._('ОК'), text_color=app.theme_cls.primary_color, on_release = self.execute_proc
                        ),
                        MDFlatButton(
                            text=app.translation._('Отмена'), text_color=app.theme_cls.primary_color, on_release = self.dialog_dismiss
                        ),
                    ],
                )
            self.dialog.open()

#форматируем текст с гиперссылками
def fill_hyperlinks(s, color):
    # для функции format
    s = s.replace('{', '{{')
    s = s.replace('}', '}}')
    r = re.compile(r"(https://[^ \r]+)")
    s = r.sub(r'[ref=\1][color={link_color}][u]\1[/u][/color][/ref]', s)
    r = re.compile(r"(http://[^ \r]+)")
    s = r.sub(r'[ref=\1][color={link_color}][u]\1[/u][/color][/ref]', s)
    s = s.format(link_color=get_hex_from_color(color))
    return s

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

custom_dialog = CustomDialog()