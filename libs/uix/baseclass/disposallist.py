#список задач
from libs.uix.baseclass.disposalsdroid import GetResult
from kivymd.button import MDIconButton, MDFlatButton, MDRaisedButton
from kivy.app import App
from kivymd.label import MDLabel
from kivymd.dialog import MDDialog
from kivy.metrics import dp
from libs.applibs.toast import toast
import threading
from kivy.factory import Factory
from kivy.clock import Clock, mainthread
from kivy.uix.recycleview import RecycleView
import time

class DisposalItem(MDFlatButton):

    _rawdata = []

    def get_rawdata(self):
        return self._rawdata

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)

        self.app = App.get_running_app()

    def set_rawdata(self, val):
        self._rawdata = val
        self.data = dict({'Number': self.rawdata[0],
                          'Theme': self.rawdata[1],
                          'Task': self.rawdata[5],
                          'ShortTask': self.rawdata[2],
                          'Receiver_id': self.rawdata[4],
                          'Sender_id': self.rawdata[3],
                          'IsComplete': self.rawdata[6],
                          'IsDisallowed': self.rawdata[8],
                          'IsReaded': self.rawdata[7]
                          })
        #номер
        self.number_label.text = '[color=ff3333]{0}[/color]'.format(self.data['Number'])
        #тема
        theme = self.data['Theme']
        if len(theme) > 30:
            theme = theme[:27] + '...'
        theme = theme.replace('\n', ' ')
        text = self.data['ShortTask'].replace('\n', ' ')
        #иконка и цвет выполнения
        if self.data['IsComplete'] == '0':
            self.icon.icon_text = 'clock'
            self.theme_label.text = '{0}'.format(theme)
            self.text_label.text = '{0}'.format(text)
        else:
            self.icon.icon_text = 'calendar-check'
            self.theme_label.text = '[color=#009933]{0}[/color]'.format(theme)
            self.text_label.text = '[color=#009933]{0}[/color]'.format(text)

        if self.data['IsReaded'] == '0':
            self.theme_label.text = '[b]{0}[/b]'.format(self.theme_label.text)
            self.text_label.text = '[b]{0}[/b]'.format(self.text_label.text)
        #иконка и шрифт отклонения
        if self.data['IsDisallowed'] == '1':
            self.icon.icon_text = 'stop'


    rawdata = property(get_rawdata, set_rawdata)

    def set_readed(self):
        try:
            GetResult('SetTaskRead', {'id': int(self.data['Number'])}, [])
        except:
            pass

    def set_disposal_params(self):
        Receiver = GetResult('getStaff', {'id': int(self.data['Receiver_id'])}, ['userName'])[0][0]
        Sender = GetResult('getStaff', {'id': int(self.data['Sender_id'])}, ['userName'])[0][0]

        self.data['Receiver'] = Receiver
        self.data['Sender'] = Sender

        self.app.screen.ids.disposal.set_params(self.data)

    #ищем следующий элемент
    def show_next(self):
        k = 0
        for w in self.parent.walk():
            if k == 1 and isinstance(w, DisposalItem):
                w.on_press()
                break
            if w == self:
                k = 1

    #ищем предыдущий элемент
    def show_prior(self):
        prior = None
        for w in self.parent.walk():
            if w == self and prior != None:
                prior.on_press()
            if isinstance(w, DisposalItem):
                prior = w

    def on_press(self):
        #считываем отправителя, получателя и добавляем к data
        self.set_disposal_params()
        self.app.manager.current = 'disposal'
        self.app.screen.ids.action_bar.title = self.app.translation._('Задача')

        #добавляем кнопки следующая, предыдущая, назад и прочитано
        self.app.screen.ids.action_bar.left_action_items = [['chevron-left', lambda x: self.app.back_screen(27)]]
        self.app.screen.ids.action_bar.right_action_items = [['read', lambda x: self.set_readed()],
                                                             ['skip-previous', lambda x: self.show_prior()],
                                                             ['skip-next', lambda x: self.show_next()]]

def get_number(i):
    return i[0]

class DisposalList(RecycleView):

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
            self.data.append({'rawdata': i,'height': 70})

        self.stop_spinner()
        toast(self.app.translation._('Загружено задач:') + ' ' + str(len(res)))

    #загрузка списка
    def load_data(self):

        Clock.schedule_once(self.start_spinner, 0)
        if self.app.current_filter == 'NotReaded':
            res = GetResult('getDisposalList', {'readed': 0},
                            ['Number', 'Theme', 'ShortTask', 'Sender_id', 'Receiver_id', 'Task', 'isExecute', 'Readed',
                             'Disabled'])
        else:
            res = GetResult('getDisposalList', {'isExecute': 0},
                           ['Number', 'Theme', 'ShortTask', 'Sender_id', 'Receiver_id', 'Task', 'isExecute', 'Readed',
                            'Disabled'])
            # res = GetResult('getDisposalList', {'isExecute': 0, 'Receiver_id': 43},
            #                  ['Number', 'Theme', 'ShortTask', 'Sender_id', 'Receiver_id', 'Task', 'isExecute', 'Readed',
            #                   'Disabled'])

        res = sorted(res, key=get_number)

        #формируем список
        self.make_list(res)

    #обновление списка задач
    def refresh_list(self):

        try:
            self.load_data()
            mythread = threading.Thread(target=self.load_data)
            mythread.start()
        except:
            #сообщение об ошибке
            content = MDLabel(
                font_style='Body1',
                text=self.app.translation._('Нет подключения, проверьте настройки!'),
                size_hint_y=None,
                valign='top')
            content.bind(texture_size=content.setter('size'))
            self.dialog = MDDialog(title="Внимание",
                                   content=content,
                                   size_hint=(.8, None),
                                   height=dp(200))

            self.dialog.add_action_button("ОК",
                                          action=lambda *x: self.dialog.dismiss())
            self.dialog.open()


