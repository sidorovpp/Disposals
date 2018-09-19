#список задач
from kivymd.list import MDList, OneLineIconListItem, ILeftBody, BaseListItem, OneLineListItem, TwoLineIconListItem, ILeftBodyTouch, TwoLineListItem
from libs.uix.baseclass.DisposalsDroid import GetResult
from kivymd.button import MDIconButton

class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    pass

class DisposalItem(TwoLineIconListItem):
    def __init__(self, icon_text, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.add_widget(IconLeftSampleWidget(icon=icon_text))

    def on_touch_up(self, touch):
        return True

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
                icon_text=icon_text
            )
            self.add_widget(item)



