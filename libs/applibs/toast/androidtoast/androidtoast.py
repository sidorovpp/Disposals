# -*- coding: utf-8 -*-

'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по услолвиям той же лицензии,
что и фреймворк Kivy.

'''

from jnius import autoclass, PythonJavaClass, java_method, cast
from android.runnable import run_on_ui_thread
import threading
import jnius

Toast = autoclass('android.widget.Toast')
context = autoclass('org.kivy.android.PythonActivity').mActivity

#заглушка для ошибки при выходе
orig_thread_run = threading.Thread.run
def thread_check_run(*args, **kwargs):
    try:
        return orig_thread_run(*args, **kwargs)
    finally:
        jnius.detach()
threading.Thread.run = thread_check_run

@run_on_ui_thread
def toast(text, length_long=False):
    duration = Toast.LENGTH_LONG if length_long else Toast.LENGTH_SHORT
    String = autoclass('java.lang.String')
    c = cast('java.lang.CharSequence', String(text))
    t = Toast.makeText(context, c, duration)
    t.show()

