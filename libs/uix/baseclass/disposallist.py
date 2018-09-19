#список задач
from kivymd.list import MDList, OneLineIconListItem, ILeftBody, BaseListItem, OneLineListItem, TwoLineIconListItem, ILeftBodyTouch, TwoLineListItem
from libs.uix.baseclass.DisposalsDroid import GetResult
from kivymd.button import MDIconButton
from kivy.app import App

class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    pass

class DisposalItem(TwoLineIconListItem):

    def __init__(self, icon_text, data, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.add_widget(IconLeftSampleWidget(icon=icon_text))
        self.data = dict({'Number':data[0],'Theme':data[1],'Task':data[5], 'Receiver':data[4], 'Sender':data[3]})

    def on_press(self):
        #считываем комментарии, отправите, получателя и добавляем к data
        s = ''
        Receiver = GetResult('getStaff', {'id': int(self.data['Receiver'])}, ['userName'])[0][0]
        Sender = GetResult('getStaff', {'id': int(self.data['Sender'])}, ['userName'])[0][0]
        Notes = GetResult('getDisposalNotes', {'disposal_id': int(self.data['Number'])}, ['DateCreate', 'UserName', 'Unnamed3'])

        for item in Notes:
            s = s + '[color=ff3333]{0}[/color]  [color=00ff33]{1}[/color]\n\n{2}\n'.format(item[0], item[1], item[2])
        self.data['Comments'] = s
        self.data['Receiver'] = Receiver
        self.data['Sender'] = Sender

        app = App.get_running_app()
        app.screen.ids.disposal.set_params(self.data)
        app.manager.current = 'disposal'
        app.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: app.back_screen(27)]]

class DisposalList(MDList):
    def __init__(self, *args, **kwargs):
        MDList.__init__(self, *args, **kwargs)
        self.refresh_list()


    def refresh_list(self):
    #обновление списка задач
        res = GetResult('getDisposalList', {'readed': 0}, ['Number', 'Theme', 'ShortTask', 'Sender_id', 'Receiver_id', 'Task', 'isExecute'])



        #self.rows = 0

        for i in res:
            #текст задачи
            if i[2] != '':
                disposal_text = i[2]
            else:
                disposal_text = 'ПУСТО'
            #иконка выполнения
            if i[6] == '0':
                icon_text = 'clock'
            else:
                icon_text = 'calendar-check'

            #номер + тема задачи
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



