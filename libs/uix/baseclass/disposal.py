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
from libs.uix.baseclass.disposalsdroid import connect_manager
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivy.utils import get_hex_from_color
from kivy.app import App
from kivy.clock import Clock, mainthread
import threading
import re
import webbrowser


class AddCommentButton(MDFloatingActionButton):

    def commit(self):
        if self.dialog.content.text.strip() != "":
            try:
                connect_manager.GetResult('SendComment', {'disposal_id': int(self.parent.ids.number.text), 'comment': self.dialog.content.text.strip()}, [])
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
    def on_ref_press(self, url):
        webbrowser.open(url)

class Task(RecycleView):
    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)
        self.data = []

class TaskLabel(Label):
    def on_ref_press(self, url):
        webbrowser.open(url)

class Disposal(Screen):

    def __init__(self, **kwargs):
        super(Disposal, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def start_spinner(self, *args):
        self.spinner.active = True

    @mainthread
    def stop_spinner(self, *args):
        self.spinner.active = False

    def load_comments(self):
        Clock.schedule_once(self.start_spinner, 0)
        self.ids.notes.data = []
        Notes = connect_manager.GetResult('getDisposalNotes', {'disposal_id': int(self.ids.number.text)}, ['DateCreate', 'UserName', 'Unnamed3'])
        if Notes != []:
            for item in Notes:
                self.notes.data.append({'text':'[color=ff3333]{0}[/color]  [color=00881D]{1}[/color]'.format(item[0], item[1])})
                #заполняем гиперлинки
                note_text = item[2]
                r = re.compile(r"(https://[^ \r]+)")
                note_text = r.sub(r'[ref=\1][color={link_color}]\1[/color][/ref]', note_text).format(link_color=get_hex_from_color(self.app.theme_cls.primary_color))
                self.notes.data.append({'text':'{0}'.format(note_text)})
            self.task.size_hint_y = 0.5
            self.notes.size_hint_y = 0.5
        else:
            #pass
            self.task.size_hint_y = 0.9
            self.notes.size_hint_y = 0.1
        self.stop_spinner()

    def set_params(self, params):
        self.ids.number.text = params['Number']
        self.ids.theme.text = params['Theme']
        self.ids.sender.text = self.manager.app.translation._('Отправитель:') + ' ' +params['Sender']
        self.ids.receiver.text = self.manager.app.translation._('Получатель:') + ' ' + params['Receiver']
        #заполняем гиперлинки
        s = params['Task']
        r = re.compile(r"(https://[^ \r]+)")
        s = r.sub(r'[ref=\1][color={link_color}]\1[/color][/ref]', s).format(
            link_color=get_hex_from_color(self.app.theme_cls.primary_color))
        #бьём текст задачи на куски по Enter
        self.ids.task.data = []
        k = s.find('\n')
        while k > 0:
            self.ids.task.data.append({'text':s[:k].replace('\r', '')})
            s = s[k+1:]
            k = s.find('\n')
        self.ids.task.data.append({'text':s})

        mythread = threading.Thread(target=self.load_comments)
        mythread.start()



