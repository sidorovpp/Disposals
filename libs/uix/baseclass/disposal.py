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
from kivymd.uix.dialog import MDDialog
from libs.uix.baseclass.disposalsdroid import connect_manager
from kivy.uix.recycleview import RecycleView, RecycleViewBehavior
from kivy.uix.label import Label
from kivy.utils import get_hex_from_color
from kivy.app import App
from kivy.clock import Clock, mainthread
from os.path import exists, join
from kivy.utils import platform
import ntpath
import os
import sys
import threading
import webbrowser
import subprocess
import plyer
from kivy.core.clipboard import Clipboard
from libs.applibs.toast import toast
from kivy.uix.behaviors import ButtonBehavior
from datetime import datetime
from libs.uix.baseclass.utils import get_date, urgency_dict, urgency_color, fill_hyperlinks
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton
from shutil import copyfile


class Content(BoxLayout):
    pass


# кнопка добавления файла
class AddFileButton(MDFloatingActionButton):

    def __init__(self, **kwargs):
        super(AddFileButton, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def add_file(self, id, filename):
        Clock.schedule_once(self.app.screen.ids.disposal.start_spinner, 0)
        try:
            byte_list = []
            with open(filename, 'rb') as f:
                # i = 1
                while True:
                    byte = f.read(1)
                    if not byte:
                        break
                    # byte_list[str(i)] = int.from_bytes(byte, 'big')
                    byte_list.append(int.from_bytes(byte, 'big'))
                    # i = i + 1
            params = {'id': id, 'object_id': 1127, 'fileName': os.path.basename(filename), 'body': byte_list}
            connect_manager.GetResult('uploadFile', params, [], prefix='TSysMethods')
            self.parent.load_files()
        finally:
            self.app.screen.ids.disposal.stop_spinner()

    def handle_selection(self, selection):
        print(selection)
        if len(selection) > 0:
            self.add_file(int(self.parent.number.text), selection[0])

    def on_press(self):
        from plyer import filechooser
        path = filechooser.open_file(title=self.app.translation._('Выберите файл'),
                                     filters=[(self.app.translation._('Все файлы'), '*.*')],
                                     on_selection=self.handle_selection
                                     )


# кнопка добавления комментария
class AddCommentButton(MDFloatingActionButton):

    def __init__(self, **kwargs):
        super(AddCommentButton, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.dialog = None

    def commit(self, inst):
        if self.dialog.content_cls.ids.comment_text.text.strip() != "":
            try:
                connect_manager.GetResult('SendComment', {'disposal_id': int(self.parent.number.text),
                                                          'comment': self.dialog.content_cls.ids.comment_text.text.strip()},
                                          [])
                connect_manager.GetResult('SetTaskRead', {'id': int(self.parent.number.text)}, [])
            except:
                pass

            self.dialog.dismiss()
            self.parent.load_comments()

    def closeDialog(self, inst):
        self.dialog.dismiss()

    def on_press(self):
        if not self.dialog:
            self.dialog = MDDialog(title=self.app.translation._('Новый комментарий'),
                                   type="custom",
                                   content_cls=Content(),
                                   buttons=[
                                       MDFlatButton
                                       (text=self.app.translation._('Сохранить'),
                                        text_color=self.theme_cls.primary_color,
                                        on_release=self.commit
                                        ),
                                       MDFlatButton
                                       (text=self.app.translation._('Отмена'),
                                        text_color=self.theme_cls.primary_color,
                                        on_release=self.closeDialog
                                        ),
                                   ],
                                   )
        self.dialog.content_cls.ids.comment_text.text = ''
        self.dialog.open()


# файлы
class Files(RecycleView, RecycleViewBehavior):
    def __init__(self, **kwargs):
        super(Files, self).__init__(**kwargs)
        self.data = []


# комментарии
class Notes(RecycleView, RecycleViewBehavior):
    def __init__(self, **kwargs):
        super(Notes, self).__init__(**kwargs)
        self.data = []


# комментарий - label
class NoteLabel(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super(NoteLabel, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def on_ref_press(self, url):
        if url[:13] == 'http://aisup/':
            if url[13:25] == 'DS_Disposals':
                self.app.screen.ids.base.number_search.text = url[26:]
                self.app.screen.ids.base.disposal_list.refresh_list({})
                self.app.manager.current = 'base'
                self.app.screen.ids.base.number_search.text = ''
            else:
                if platform == 'android':
                    toast(self.app.translation._('Не поддерживается!'))
        else:
            webbrowser.open(url)

    def on_release(self):
        # if self.collide_point(*touch.pos):
        Clipboard.copy(self.text)
        if platform == 'android':
            toast(self.app.translation._('Скопировано в буфер'))
        return True


# текст задачи
class Task(RecycleView):
    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)
        self.data = []


# текст задачи - label
class TaskLabel(ButtonBehavior, Label):

    def __init__(self, **kwargs):
        super(TaskLabel, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def on_release(self):
        # if self.collide_point(*touch.pos):
        Clipboard.copy(self.text)
        if platform == 'android':
            toast(self.app.translation._('Скопировано в буфер'))
        return True

    def camera_callback(self, filepath):
        if exists(filepath):
            print('saved')
        else:
            print('unable to save.')

    def open_file(self, filename):
        # webbrowser.open_new('file://' + filename)
        if platform == 'android':
            try:
                import jnius
                import mimetypes
                # don't work
                '''
                from jnius import autoclass
                from android import mActivity
                mime_type, _ = mimetypes.guess_type(filename)
                File = autoclass('java.io.File')

                Intent = autoclass('android.content.Intent')
                FileProvider = autoclass('android.support.v4.content.FileProvider')

                uri = FileProvider.getUriForFile(
                    mActivity, 'ru.mrcpp.disposals.fileprovider', File(filename)
                )

                intent = Intent()
                intent.setAction(Intent.ACTION_VIEW)
                intent.setDataAndType(uri, mime_type)
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

                mActivity.startActivity(intent)
                '''
                # old version
                PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
                Intent = jnius.autoclass('android.content.Intent')
                Uri = jnius.autoclass('android.net.Uri')

                mimetype = mimetypes.guess_type(filename)[0]
                image_uri = 'file://' + filename

                intent = Intent()
                intent.setAction(Intent.ACTION_VIEW)
                intent.setDataAndType(Uri.parse(image_uri), mimetype)
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                currentActivity = jnius.cast('android.app.Activity', PythonActivity.mActivity)
                currentActivity.startActivity(intent)

                # camera
                # from plyer import camera

                # file_name = join(self.app.public_dir, 'test.jpg')
                # camera.take_picture(filename=file_name, on_complete = self.camera_callback)

            except Exception as error:
                print(str(error))
        elif sys.platform.startswith('darwin'):
            subprocess.call(('open', filename))
        elif os.name == 'nt':  # For Windows
            os.startfile(filename)
        else:  # For Linux, Mac, etc.
            subprocess.call(('xdg-open', filename))

    def show_file(self, id, filename):
        Clock.schedule_once(self.app.screen.ids.disposal.start_spinner, 0)

        try:
            # загружаем файл
            res = connect_manager.GetResult('getFile', {'id': id}, [], prefix='TSysMethods')

            # сохраняем в пользовательскую папку
            ext = os.path.splitext(filename)[1]
            ext = ext.replace('docx', 'doc')
            ext = ext.replace('xlsx', 'xls')
            filename_new = join(self.app.directory, 'temp' + ext)
            # filename = join(self.app.public_dir, 'temp' + ext)
            tfp = open(filename_new, 'wb')
            with tfp:
                tfp.write(bytes(res[0]))
                # копирую на карту
            copyfile(filename_new,
                     join(self.app.public_dir, 'temp' + ext)
                     )
            copyfile(filename_new,
                     join(plyer.storagepath.get_downloads_dir(), filename)
                     )
        finally:
            self.app.screen.ids.disposal.stop_spinner()

        # запускаем файл
        if platform == 'android':
            toast(self.app.translation._('Скопировано в Загрузки'))
            # self.open_file(plyer.storagepath.get_downloads_dir())
        else:
            # self.open_file(filename)
            self.open_file(plyer.storagepath.get_downloads_dir())

    def on_ref_press(self, url):
        if url[:13] == 'http://aisup/':
            if url[13:25] == 'DS_Disposals':
                self.app.screen.ids.base.number_search.text = url[26:]
                self.app.screen.ids.base.disposal_list.refresh_list({})
                self.app.manager.current = 'base'
                self.app.screen.ids.base.number_search.text = ''
            else:
                if platform == 'android':
                    toast(self.app.translation._('Не поддерживается!'))

        else:
            path = url[:url.find(':')]
            if path.isnumeric():
                mythread = threading.Thread(target=self.show_file,
                                            kwargs={'id': int(path), 'filename': url[url.find(':') + 1:]})
                mythread.start()
                # self.show_file(int(path), url[url.find(':') + 1:])
            else:
                webbrowser.open(url)


# форма задачи
class Disposal(Screen):

    def __init__(self, **kwargs):
        super(Disposal, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def start_spinner(self, *args):
        self.spinner.active = True

    @mainthread
    def stop_spinner(self, *args):
        self.spinner.active = False

    def set_size(self):
        if self.notes.data:
            self.notes_splitter.size_hint_y = 0.4
            self.notes_splitter.min_size = 100
        else:
            self.notes_splitter.size_hint_y = 0.01
            self.notes_splitter.min_size = 0
        if self.files.data:
            self.files_splitter.size_hint_y = 0.3
            self.files_splitter.min_size = 100
        else:
            self.files_splitter.size_hint_y = 0.01
            self.files_splitter.min_size = 0

        self.task.size_hint_y = 1 - (self.notes_splitter.size_hint_y + self.files_splitter.size_hint_y)

    def load_comments(self):
        # добавляем комментарии
        Clock.schedule_once(self.start_spinner, 0)
        self.notes.data = []
        notes_data = connect_manager.GetResult('getDisposalNotes', {'disposal_id': int(self.ids.number.text)},
                                          ['DateCreate', 'UserName', 'Unnamed3'])
        if notes_data:
            for item in notes_data:
                self.notes.data.append(
                    {'text': '[color=ff3333]{0}[/color]  [color=00881D]{1}[/color]'.format(item[0], item[1])})
                note_text = fill_hyperlinks(item[2], self.app.theme_cls.primary_color)
                self.notes.data.append({'text': '{0}'.format(note_text)})
        self.set_size()
        self.stop_spinner()

    def load_files(self):
        # добавляем файлы
        Clock.schedule_once(self.start_spinner, 0)
        self.files.data = []
        files_data = connect_manager.GetResult('getFileList', {'object_id': 1127, 'line_id': int(self.ids.number.text)},
                                          ['id', 'FileName'], prefix='TSysMethods')
        for item in files_data:
            self.files.data.append({'text': r'[ref={url}][color={link_color}][u]{text}[/u][/color][/ref]'.format(
                url=item[0] + ':' + ntpath.basename(item[1]),
                text=ntpath.basename(item[1]),
                link_color=get_hex_from_color(self.app.theme_cls.primary_color)
            )})
        self.set_size()
        self.stop_spinner()

    def refresh_view(self, *args):
        self.files.refresh_from_data()
        self.notes.refresh_from_data()

    def set_params(self, params):
        self.ids.number.text = params['Number']
        self.ids.urgency.text = urgency_dict[params['Urgency_id']]
        # конвертирую цвет
        h = urgency_color[params['Urgency_id']].lstrip('#')
        c = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        self.ids.urgency.color = [c[0] / 255, c[1] / 255, c[2] / 255, 1]

        self.ids.theme.text = params['Theme']
        self.ids.sender.text = self.manager.app.translation._('Отправитель:') + ' ' + params['Sender']
        self.ids.receiver.text = self.manager.app.translation._('Получатель:') + ' ' + params['Receiver']

        if params['IsComplete'] == '0':
            if (params['PlanDateTo'] != '') and (datetime.now() > get_date(params['PlanDateTo'])):
                self.ids.theme.color = [1, 0, 0, 1]
            else:
                self.ids.theme.color = [0, 0, 0, 1]
        else:
            if params['IsConfirmed'] == '':
                self.ids.theme.color = [0, 1, 0, 1]
            else:
                self.ids.theme.color = [0, 0, 1, 1]

        # заполняем гиперлинки
        s = fill_hyperlinks(params['Task'], self.app.theme_cls.primary_color)

        # бьём текст задачи на куски по Enter
        self.ids.task.data = []
        k = s.find('\n')
        while k > 0:
            self.ids.task.data.append({'text': s[:k].replace('\r', '')})
            s = s[k + 1:]
            k = s.find('\n')
        self.task.data.append({'text': s})

        # загружаем файлы
        self.load_files()

        # убрал загрузку потоком, иногда отваливалось при прорисовке
        self.load_comments()
        # запускаем поток загрузки комментариев
        # mythread = threading.Thread(target=self.load_comments)
        # mythread.start()
