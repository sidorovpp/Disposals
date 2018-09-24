# -*- coding: utf-8 -*-
#
# This file created with KivyCreatorProject
# <https://github.com/HeaTTheatR/KivyCreatorProgect
#
# Copyright © 2017 Easy
#
# For suggestions and questions:
# <kivydevelopment@gmail.com>
#
# LICENSE: MIT

from kivy.uix.screenmanager import Screen
from kivymd.button import MDFloatingActionButton
from kivymd.dialog import MDDialog
from kivymd.textfields import MDTextField
from kivy.metrics import dp
from libs.uix.baseclass.DisposalsDroid import GetResult
from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label

class AddCommentButton(MDFloatingActionButton):

    def commit(self):
        if self.dialog.content.text.strip() != "":
            try:
                GetResult('SendComment', {'disposal_id': int(self.parent.ids.number.text), 'comment': self.dialog.content.text.strip()}, [])
            except:
                pass

            self.dialog.dismiss()
            self.parent.load_comments()

    def on_press(self):
        content = MDTextField()
        content.multiline = True
        content.hint_text = "Введите комментарий"
        content.focus = True
        self.dialog = MDDialog(title="Новый комментарий",
                               content=content,
                               size_hint=(.8, None),
                               height=dp(400))

        self.dialog.add_action_button("Сохранить",
                                      action=lambda *x: self.commit())
        self.dialog.add_action_button("Отмена",
                                      action=lambda *x: self.dialog.dismiss())
        self.dialog.open()


class Notes(RecycleView):
    def __init__(self, **kwargs):
        super(Notes, self).__init__(**kwargs)
        self.data = []

class NoteLabel(Label):
    pass

class Disposal(Screen):


    def load_comments(self):
        self.ids.spinner.active = True
        try:
            self.ids.notes.data.clear()
            Notes = GetResult('getDisposalNotes', {'disposal_id': int(self.ids.number.text)}, ['DateCreate', 'UserName', 'Unnamed3'])
            for item in Notes:
                self.ids.notes.data.append({'text':'[color=ff3333]{0}[/color]  [color=00881D]{1}[/color]\n\n{2}\n\n'.format(item[0], item[1], item[2])})
        finally:
            self.ids.spinner.active = False

    def set_params(self, params):
        app = App.get_running_app()
        self.ids.number.text = params['Number']
        self.ids.theme.text = params['Theme']
        self.ids.task.text = params['Task']
        self.ids.sender.text = app.translation._('Отправитель:') + ' ' +params['Sender']
        self.ids.receiver.text = app.translation._('Получатель:') + ' ' + params['Receiver']
        self.load_comments()

    def on_leave(self, *args):
        app = App.get_running_app()
        app.screen.ids.action_bar.right_action_items = []
        app.screen.ids.base.ids.disposal_list.clear_widgets()
        app.screen.ids.base.ids.disposal_list.refresh_list()

