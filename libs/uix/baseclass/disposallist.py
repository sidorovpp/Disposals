# список задач
from libs.uix.baseclass.disposalsdroid import GetResult
from kivymd.button import MDIconButton, MDFlatButton, MDRaisedButton
from kivy.app import App
from kivymd.label import MDLabel
from kivymd.dialog import MDDialog
from kivy.metrics import dp
from libs.applibs.toast import toast
import threading
from kivy.clock import Clock, mainthread
from kivy.uix.recycleview import RecycleView
from datetime import datetime
import time


class DisposalItem(MDFlatButton):

    _data = []

    def get_data(self):
        return self._data

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)

        self.app = App.get_running_app()

    def set_data(self, val):
        def get_date(str):
            if len(str) > 10:
                return datetime.strptime(str, '%d.%m.%Y %H:%M:%S')
            else:
                return datetime.strptime(str, '%d.%m.%Y')

        self._data = val
        # номер
        self.number_label.text = '[color=#003380]{0}[/color]'.format(self.data['Number'])
        # тема
        theme = self.data['Theme']
        theme = theme.replace('\n', ' ')
        text = self.data['Task'].replace('\n', ' ')
        self.theme_label.text = '{0}'.format(theme)
        self.text_label.text = '{0}'.format(text)
        # иконка и цвет выполнения
        if self.data['IsComplete'] == '0':
            if (self.data['PlanDateTo'] != '') and (datetime.now() > get_date(self.data['PlanDateTo'])):
                self.icon.text_color = [1, 0, 0, 1]
            else:
                self.icon.text_color = [0, 0, 1, 1]
            self.icon.icon_text = 'clock'
        else:
            self.icon.icon_text = 'calendar-check'
            self.icon.text_color = [0, 1, 0, 1]
            #self.theme_label.text = '[color=#009933]{0}[/color]'.format(theme)
            #self.text_label.text = '[color=#009933]{0}[/color]'.format(text)

        if self.data['IsReaded'] == '0':
            self.theme_label.text = '[b]{0}[/b]'.format(self.theme_label.text)
            self.text_label.text = '[b]{0}[/b]'.format(self.text_label.text)
        # иконка и шрифт отклонения
        if self.data['IsDisallowed'] == '1':
            self.icon.icon_text = 'stop'

    data = property(get_data, set_data)

    def set_readed(self):
        try:
            number = self.app.screen.ids.disposal.number.text
            GetResult('SetTaskRead', {'id': int(number)}, [])
        except:
            pass

    def set_disposal_params(self, item_data):
        Receiver = GetResult('getStaff', {'id': int(item_data['Receiver_id'])}, ['userName'])[0][0]
        Sender = GetResult('getStaff', {'id': int(item_data['Sender_id'])}, ['userName'])[0][0]

        item_data['Receiver'] = Receiver
        item_data['Sender'] = Sender

        self.app.screen.ids.disposal.set_params(item_data)

    # ищем следующий элемент
    def show_next(self):
        number = self.app.screen.ids.disposal.number.text

        for i in self.parent.parent.data:
            if i['data']['Number'] > number:
                self.set_disposal_params(i['data'])
                break

    # ищем предыдущий элемент
    def show_prior(self):
        number = self.app.screen.ids.disposal.number.text

        for i in self.parent.parent.data[::-1]:
            if i['data']['Number'] < number:
                self.set_disposal_params(i['data'])
                break

    def on_release(self):
        # считываем отправителя, получателя и добавляем к data
        self.set_disposal_params(self.data)
        self.app.manager.current = 'disposal'
        self.app.screen.ids.action_bar.title = self.app.translation._('Задача')

        # добавляем кнопки следующая, предыдущая, назад и прочитано
        self.app.screen.ids.action_bar.left_action_items = [['chevron-left', lambda x: self.app.back_screen(27)]]
        self.app.screen.ids.action_bar.right_action_items = [['read', lambda x: self.set_readed()],
                                                             ['skip-previous', lambda x: self.show_prior()],
                                                             ['skip-next', lambda x: self.show_next()]]


def get_number(i):
    return i[0]


class DisposalList(RecycleView):

    StaffID = None

    def __init__(self, *args, **kwargs):
        super(DisposalList, self).__init__(*args, **kwargs)
        self.app = App.get_running_app()

    def start_spinner(self, *args):
        self.app.screen.ids.base.spinner.active = True

    @mainthread
    def stop_spinner(self, *args):
        self.app.screen.ids.base.spinner.active = False

    @mainthread
    def make_list(self, res):
        self.data = []

        for i in res:
            item = dict({'Number': i[0],
                        'Theme': i[1],
                        'Task': i[5],
                        'ShortTask': i[2],
                        'Receiver_id': i[4],
                        'Sender_id': i[3],
                        'IsComplete': i[6],
                        'IsDisallowed': i[8],
                        'IsReaded': i[7],
                        'PlanDateTo': i[9]
                        })

            self.data.append({'data': item,'height': dp(70)})

        self.stop_spinner()
        #toast(self.app.translation._('Загружено задач:') + ' ' + str(len(res)))

    @mainthread
    def show_connect_error(self):
        self.stop_spinner()
        content = MDLabel(
            font_style='Body1',
            text=self.app.translation._('Нет подключения, проверьте настройки!'),
            size_hint_y=None,
            valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title=self.app.translation._('Внимание'),
                               content=content,
                               size_hint=(.8, None),
                               height=dp(200))

        self.dialog.add_action_button("ОК",
                                      action=lambda *x: self.dialog.dismiss())
        self.dialog.open()

    # загрузка списка
    def load_data(self):

        Clock.schedule_once(self.start_spinner, 0)
        try:
            if self.StaffID == None:
                self.StaffID = GetResult('getStaffID', {}, [])

            Columns = ['Number', 'Theme', 'ShortTask', 'Sender_id', 'Receiver_id', 'Task', 'isExecute', 'Readed', 'Disabled', 'PlanDateTo']
            if self.app.current_filter == 'NotReaded':
                res = GetResult('getDisposalList', {'readed': 0}, Columns)
            elif self.app.current_filter == 'FromMe':
                res = GetResult('getDisposalList', {'isExecute': 0, 'Sender_id': self.StaffID}, Columns)
            elif self.app.current_filter == 'ToMe':
                res = GetResult('getDisposalList', {'isExecute': 0, 'Receiver_id': self.StaffID}, Columns)
            else:
                res = GetResult('getDisposalList', {'isExecute': 0}, Columns)
                # res = GetResult('getDisposalList', {'isExecute': 0, 'Receiver_id': 43},
                #                  ['Number', 'Theme', 'ShortTask', 'Sender_id', 'Receiver_id', 'Task', 'isExecute', 'Readed',
                #                   'Disabled'])


            res = sorted(res, key=get_number)

            # формируем список
            self.make_list(res)
        except:
            # сообщение об ошибке
            self.show_connect_error()

    # обновление списка задач
    def refresh_list(self):

        mythread = threading.Thread(target=self.load_data)
        mythread.start()


