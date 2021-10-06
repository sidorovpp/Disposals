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
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.textfield import MDTextField
from kivy.app import App
from kivy.clock import Clock

#кнопка добавления задачи
class AddDisposalButton(MDFloatingActionButton):
    def on_press(self):
        app = App.get_running_app()
        app.manager.current = 'disposal_form'

class SearchTextField(MDTextField):

    def start_select(self, *args):
        if self.text != '':
            self.select_all()

    def on_focus(self, *args):
        super().on_focus(*args)
        if args[1] == True:
            Clock.schedule_once(self.start_select, 0.1)


class BaseScreen(Screen):

    def press(self, keyboard, keycode, text, modifiers):
        if keycode == 'enter':
            self.refresh_list()

    def refresh_list(self):
        #self.ids.disposal_list.clear_widgets()
        self.disposal_list.refresh_list(params={})

    def add_refresh_button(self):
        try:
            self.manager.screen.ids.action_bar.right_action_items = [['refresh', lambda x: self.refresh_list()]]
        except:
            pass

    def on_enter(self, *args):
        self.add_refresh_button()