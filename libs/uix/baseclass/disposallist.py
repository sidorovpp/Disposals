#список задач
from kivymd.list import MDList, OneLineIconListItem, ILeftBody, BaseListItem, OneLineListItem, TwoLineIconListItem, ILeftBodyTouch, TwoLineListItem
from libs.uix.baseclass.DisposalsDroid import GetResult
from kivymd.button import MDIconButton
from kivy.app import App
from kivymd.label import MDLabel
from kivymd.dialog import MDDialog
from kivy.metrics import dp

class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    pass

class DisposalItem(TwoLineIconListItem):

    def __init__(self, icon_text, data, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.add_widget(IconLeftSampleWidget(icon=icon_text))
        self.data = dict({'Number':data[0],'Theme':data[1],'Task':data[5], 'Receiver_id':data[4], 'Sender_id':data[3]})

    def set_readed(self):
        try:
            GetResult('SetTaskRead', {'id': int(self.data['Number'])}, [])
        except:
            pass

    def on_press(self):
        #считываем комментарии, отправите, получателя и добавляем к data
        s = ''
        Receiver = GetResult('getStaff', {'id': int(self.data['Receiver_id'])}, ['userName'])[0][0]
        Sender = GetResult('getStaff', {'id': int(self.data['Sender_id'])}, ['userName'])[0][0]

        self.data['Receiver'] = Receiver
        self.data['Sender'] = Sender

        app = App.get_running_app()
        app.screen.ids.disposal.set_params(self.data)
        app.manager.current = 'disposal'
        app.screen.ids.action_bar.title = app.translation._('Задача')
        app.screen.ids.action_bar.left_action_items = [['chevron-left', lambda x: app.back_screen(27)]]
        app.screen.ids.action_bar.right_action_items = [['read', lambda x: self.set_readed()]]

class DisposalList(MDList):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.refresh_list()

    def refresh_list(self):
    #обновление списка задач
        def get_number(i):
            return i[0]
        try:
            res = GetResult('getDisposalList', {'readed': 0}, ['Number', 'Theme', 'ShortTask', 'Sender_id', 'Receiver_id', 'Task', 'isExecute'])


            res = sorted(res, key=get_number)
            for i in res:
                # текст задачи
                if i[2] != '':
                    disposal_text = i[2]
                else:
                    disposal_text = 'ПУСТО'
                # иконка выполнения
                if i[6] == '0':
                    icon_text = 'clock'
                else:
                    icon_text = 'calendar-check'

                # номер + тема задачи
                theme_text = (i[0] + ' ' + i[1])
                if len(theme_text) > 30:
                    theme_text = theme_text[:27] + '...'

                item = DisposalItem(
                    text=theme_text,
                    secondary_text=disposal_text,
                    icon_text=icon_text,
                    data=i
                )
                self.add_widget(item)
        except:
            #сообщение об ошибке
            app = App.get_running_app()
            content = MDLabel(
                font_style='Body1',
                text=app.translation._('Нет подключения, проверьте настройки!'),
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


