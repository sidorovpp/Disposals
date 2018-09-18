#список задач
from kivymd.list import MDList, OneLineIconListItem, ILeftBody, BaseListItem, OneLineListItem, ThreeLineListItem
from libs.uix.baseclass.DisposalsDroid import GetResult


class DisposalList(MDList):
    def __init__(self, *args, **kwargs):
        MDList.__init__(self, *args, **kwargs)
        res = GetResult('getDisposalList', {'readed': 0}, ['Number', 'ShortTask', 'Sender_id', 'Receiver_id', 'Task'])

        for i in res:
            self.add_widget(
                ThreeLineListItem(
                    text = i[0],
                    secondary_text = i[1]
                )
            )