#список задач
from kivymd.list import MDList, OneLineIconListItem, ILeftBody, BaseListItem, OneLineListItem, TwoLineIconListItem, ILeftBodyTouch, TwoLineListItem
from libs.uix.baseclass.disposalsdroid import GetResult
from kivymd.button import MDIconButton
from kivy.app import App
from kivymd.label import MDLabel
from kivymd.dialog import MDDialog
from kivy.metrics import dp
from libs.applibs.toast import toast
import threading
from kivy.factory import Factory
from kivy.clock import Clock, mainthread
import time

class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    pass

class DisposalItem(TwoLineIconListItem):

    def __init__(self, data, *args, **kwargs):
        super().__init__( *args, **kwargs)

        self.app = App.get_running_app()

        # иконка и цвет выполнения
        if data[6] == '0':
            icon_text = 'clock'
        else:
            icon_text = 'calendar-check'
            self.secondary_theme_text_color = 'Custom'
            self.secondary_text_color = [0.2, 0.5, 0.2, 1]
            self.ripple_color = [0.2, 0.5, 0.2, 1]

        #иконка и шрифт отклонения
        if data[8] == '1':
            icon_text = 'stop'
            self.secondary_theme_text_color = 'Custom'
            self.secondary_text_color = [1, 0, 0, 1]

        self.add_widget(IconLeftSampleWidget(icon=icon_text))

        self.data = dict({'Number':data[0],'Theme':data[1],'Task':data[5], 'Receiver_id':data[4], 'Sender_id':data[3]})

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

class DisposalList(MDList):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = App.get_running_app()

    def show_spinner(self, *args):
        self.app.screen.ids.base.ids.spinner.active = True

    #загрузка списка
    def load_data(self):

        if self.app.current_filter == 'NotReaded':
            res = GetResult('getDisposalList', {'readed': 0},
                            ['Number', 'Theme', 'ShortTask', 'Sender_id', 'Receiver_id', 'Task', 'isExecute', 'Readed',
                             'Disabled'])
        else:
            res = GetResult('getDisposalList', {'isExecute': 0, 'Receiver_id': 43},
                            ['Number', 'Theme', 'ShortTask', 'Sender_id', 'Receiver_id', 'Task', 'isExecute', 'Readed',
                             'Disabled'])

        res = sorted(res, key=get_number)
        for i in res:
            # текст задачи
            if i[2] != '':
                disposal_text = i[2]
            else:
                disposal_text = 'ПУСТО'

            # номер + тема задачи
            theme_text = (i[0] + ' ' + i[1])
            if len(theme_text) > 30:
                theme_text = theme_text[:27] + '...'

            # позиция задачи
            item = DisposalItem(
                text=theme_text,
                secondary_text=disposal_text,
                data=i
            )
            self.add_widget(item)
            self.app.screen.ids.base.ids.spinner.active = False
            toast(self.app.translation._('Загружено задач:') + ' ' + str(len(res)))

    #обновление списка задач
    def refresh_list(self):

        try:
            #self.load_data()
            mythread = threading.Thread(target=self.load_data())
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


