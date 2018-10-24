from libs.uix.baseclass.disposalsdroid import connect_manager
from kivy.app import App
from kivymd.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from libs.applibs.dialogs import card
from libs.uix.lists import Lists

class DisposalForm(Screen):

    CurrentStaff = None
    CurrentStaffID = None

    def on_enter(self, *args):
        self.manager.screen.ids.action_bar.right_action_items = []

    #поиск сотрудника по тексту
    def search_staff(self, *args):
        def select_staff(staff):
            for item in self.res:
                if item[0] == staff:
                    self.CurrentStaffID = item[1]
                    self.CurrentStaff = item[0]
                    self.receiver.text = self.CurrentStaff
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

    #сохранение задачи
    def save(self, *args):
        self.manager.current = 'base'

    #отмена
    def cancel(self, *args):
        self.manager.current = 'base'



