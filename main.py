# -*- coding: utf-8 -*-
#
# This file created with KivyCreatorProject
# <https://github.com/HeaTTheatR/KivyCreatorProgect
#
# Copyright В© 2017 Easy
#
# For suggestions and questions:
# <kivydevelopment@gmail.com>
# 
# LICENSE: MIT


import os
import sys
import traceback
from shutil import copyfile
from os.path import join

directory = os.path.split(os.path.abspath(sys.argv[0]))[0]
#sys.path.insert(0, os.path.join(directory, 'libs/applibs'))

#try:
import webbrowser
try:
    import six.moves.urllib
except ImportError:
    pass

import kivy
kivy.require('1.9.2')

from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'system')
Config.set('kivy', 'log_enable', 0)

from kivy import platform
if platform == 'android':
    from plyer import orientation
    orientation.set_sensor(mode='portrait')

from libs.applibs.bugreporter import BugReporter
#except Exception:
#    traceback.print_exc(file=open(os.path.join(directory, 'error.log'), 'w'))
#    sys.exit(1)


__version__ = '0.1'


def main():
    """
    def create_error_monitor():
        class _App(MDApp):
            theme_cls = ThemeManager()
            theme_cls.primary_palette = 'BlueGrey'

            def build(self):
                box = BoxLayout()
                box.add_widget(report)
                return box
        app = _App()
        app.run()
    """
    app = None

    #from loadplugin import load_plugin
    from disposals import Disposals

    app = Disposals()
    #load_plugin(app, __version__)
    app.run()
    #except Exception:
        #from kivy.app import App
        #from kivy.uix.boxlayout import BoxLayout

    #    text_error = traceback.format_exc()
    #    traceback.print_exc(file=open(os.path.join(directory, 'error.log'), 'w'))
        #copyfile(join(app.directory, 'error.log'),
        #         join(app.user_data_dir, 'error.log')
        #         )

        #if app:
        #    try:
        #        app.stop()
        #    except AttributeError:
        #        app = None


if __name__ in ('__main__', '__android__'):
    main()
