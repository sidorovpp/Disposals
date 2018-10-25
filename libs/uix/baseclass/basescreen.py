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
from kivy.app import App

#кнопка добавления задачи
class AddDisposalButton(MDFloatingActionButton):
    def on_press(self):
        app = App.get_running_app()
        app.manager.current = 'disposal_form'
        app.screen.ids.action_bar.title = \
            app.translation._('Новая задача')
        app.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: app.back_screen(27)]]

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