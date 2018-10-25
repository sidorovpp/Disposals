from libs.uix.baseclass.disposalsdroid import connect_manager
from kivy.app import App
from kivy.uix.screenmanager import Screen
from libs.applibs.dialogs import card
from libs.uix.lists import Lists
from libs.uix.baseclass.utils import show_dialog


class DisposalForm(Screen):

    ReceiverStaffID = None

    def __init__(self, *args, **kwargs):
        super(DisposalForm, self).__init__(*args, **kwargs)
        self.app = App.get_running_app()

    def on_enter(self, *args):
        self.manager.screen.ids.action_bar.right_action_items = []

    #поиск сотрудника по тексту
    def search_staff(self, *args):
        def select_staff(staff):
            for item in self.res:
                if item[0] == staff:
                    self.receiver.text = staff
                    self.ReceiverStaffID = item[1]
                    self.receiver.foreground_color = (0,0,1,1)
                    self.window_staff.dismiss()

        if len(self.receiver.text) < 3:
            return

        self.res = connect_manager.GetResult('getStaff', {'name':'%%' + self.receiver.text + '%%'}, ['userName', '_id'])
        staff = {}
        for item in self.res:
            staff[item[0]] = ['staff', item[0] == self.receiver.text]

        self.window_staff = card(
            Lists(
                dict_items=staff,
                events_callback=select_staff, flag='one_select_check'
            ),
            size=(.85, .55)
            )

        self.window_staff.open()

    #обработчик текста получателя
    def receiver_change(self, text):
        self.ReceiverStaffID = None
        self.receiver.foreground_color = (1, 0, 0, 1)

    #важность
    def get_urgency(self):
        if self.urgency.value == 5:
            u = 6
        else:
            u = 5 - self.urgency.value
        return u

    #сохранение задачи
    def save(self, *args):
        if self.ReceiverStaffID == None:
            self.receiver.focus = True
            return
        if self.theme.text.strip() == '':
            self.theme.focus = True
            return
        if self.task.text.strip() == '':
            self.task.focus = True
            return

        #добавляем задачу
        try:
            res = connect_manager.GetResult('addDisposal', {'Sender': connect_manager.StaffID,
                                                            'Receiver': self.ReceiverStaffID,
                                                            'Theme': self.theme.text.strip(),
                                                            'Zadanie': self.task.text.strip(),
                                                            'Urgency': self.get_urgency()}, ['id'])
        except Exception as error:
            show_dialog(self.app.translation._('Ошибка'), str(error), None, True)
        self.app.screen.ids.base.disposal_list.refresh_list(params={'Number':res[0][0]})
        self.manager.current = 'base'


    #отмена
    def cancel(self, *args):
        self.manager.current = 'base'



