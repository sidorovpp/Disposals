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
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

class BaseScreen(Screen):

    def refresh_list(self):
        self.ids.disposal_list.clear_widgets()
        self.ids.disposal_list.refresh_list()

    def add_refresh_button(self):
        try:
            self.manager.screen.ids.action_bar.right_action_items = [['refresh', lambda x: self.refresh_list()]]
        except:
            pass

    def on_enter(self, *args):
        self.add_refresh_button()