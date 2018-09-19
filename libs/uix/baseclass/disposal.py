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


class Disposal(Screen):
    def set_params(self, params):
        self.ids.number.text = params['Number']
        self.ids.theme.text = params['Theme']
        self.ids.task.text = params['Task']
        self.ids.comments.text = params['Comments']
        self.ids.sender.text = 'Отправитель: ' + params['Sender']
        self.ids.receiver.text = 'Получатель : ' + params['Receiver']

