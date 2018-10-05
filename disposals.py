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
from ast import literal_eval
from os.path import join
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import ConfigParser
from kivy.logger import PY2
from kivy.utils import get_hex_from_color
from kivy.properties import ObjectProperty, StringProperty
from main import __version__
from libs.translation import Translation
from libs.uix.baseclass.startscreen import StartScreen
from libs.uix.lists import Lists
from kivymd.theming import ThemeManager
from libs.applibs.dialogs import card
import os.path
from shutil import copyfile
from kivy.utils import platform
from libs.uix.baseclass.disposalsdroid import connect_manager
from libs.uix.baseclass.disposallist import DisposalList


class Disposals(App):

    title = 'Задачи ВКБ'
    icon = 'icon.png'
    nav_drawer = ObjectProperty()
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Blue'
    lang = StringProperty('ru')

    def __init__(self, **kvargs):
        super(Disposals, self).__init__(**kvargs)
        Window.bind(on_keyboard=self.events_program)
        Window.soft_input_mode = 'below_target'

        self.list_previous_screens = ['base']
        self.window = Window
        self.config = ConfigParser()
        self.sysconfig = ConfigParser()
        self.manager = None
        self.window_language = None
        self.window_filter = None
        self.exit_interval = False
        self.dict_language = literal_eval(
            open(
                os.path.join(self.directory, 'data', 'locales', 'locales.txt')).read()
        )
        self.translation = Translation(
            self.lang, 'Ttest', os.path.join(self.directory, 'data', 'locales')
        )
        self.filter_items = {'NotReaded': self.translation._('Непрочитанные'),
                             'FromMe': self.translation._('Задачи от меня'),
                             'ToMe': self.translation._('Задачи на меня'),
                             'MyNotComplete': self.translation._('Все в работе')}

    def build(self):

        #грузим файл конфигураций из пользовательской папки, если есть
        try:
            copyfile(join(self.user_data_dir, 'disposals.ini'),
                     join(self.directory, 'disposals.ini')
                     )
        except:
            pass
        self.set_value_from_config()
        self.load_all_kv_files(join(self.directory, 'libs', 'uix', 'kv'))
        self.screen = StartScreen()
        #менеджер окон
        self.manager = self.screen.ids.manager
        #для упрощения доступа к screen
        self.manager.screen = self.screen
        #для упрощения доступа к app
        self.manager.app = self
        #меню
        self.nav_drawer = self.screen.ids.nav_drawer
        self.screen.ids.base.add_refresh_button()

        #стартуем сервис уведомлений
        self.start_service()
        #обвноляем список
        self.refresh_list()

        return self.screen

    def get_application_config(self):
        return super(Disposals, self).get_application_config(
                        '{}/%(appname)s.ini'.format(self.directory))

    def build_config(self, config):

        config.adddefaultsection('General')
        config.setdefault('General', 'language', 'ru')
        config.setdefault('General', 'ip', '77.233.5.22')
        config.setdefault('General', 'user', 'user')
        config.setdefault('General', 'password', 'password')
        config.setdefault('General', 'filter', 'NotReaded')
        config.setdefault('General', 'sms', '')

    def set_value_from_config(self):

        #пользовательские настройки
        self.config.read(join(self.directory, 'disposals.ini'))
        self.lang = self.config.get('General', 'language')
        self.current_filter = self.config.get('General', 'filter')
        connect_manager.server = self.config.get('General', 'ip')
        connect_manager.username = self.config.get('General', 'user')
        connect_manager.password = self.config.get('General', 'password')
        connect_manager.sms = self.config.get('General', 'sms')

        #системные настройки
        self.sysconfig.read(join(self.directory, 'server.ini'))
        connect_manager.sysusername = self.sysconfig.get('Access', 'user')
        connect_manager.syspassword = self.sysconfig.get('Access', 'password')

        #инициализируем соединение
        connect_manager.InitConnect()

        #скидываем копию конфигураций в пользовательскую папку
        try:
            copyfile(join(self.directory, 'disposals.ini'),
                     join(self.user_data_dir, 'disposals.ini')
                     )
        except:
            pass

    def test(self, *args):
        if platform == 'android':
            import jnius
            Context = jnius.autoclass('android.content.Context')
            Intent = jnius.autoclass('android.content.Intent')
            PendingIntent = jnius.autoclass('android.app.PendingIntent')
            AndroidString = jnius.autoclass('java.lang.String')
            NotificationBuilder = jnius.autoclass('android.app.Notification$Builder')
            Notification = jnius.autoclass('android.app.Notification')
            service_name = 'S1'
            package_name = 'com.something'
            service = jnius.autoclass('org.kivy.android.PythonService').mService
            PythonActivity = jnius.autoclass('org.kivy.android' + '.PythonActivity')
            app_context = service.getApplication().getApplicationContext()
            notification_builder = NotificationBuilder(app_context)
            title = AndroidString("EzTunes".encode('utf-8'))
            message = AndroidString("Ready to play music.".encode('utf-8'))
            notification_intent = Intent(app_context, PythonActivity)
            notification_intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP |
                                         Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_NEW_TASK)
            notification_intent.setAction(Intent.ACTION_MAIN)
            notification_intent.addCategory(Intent.CATEGORY_LAUNCHER)
            intent = PendingIntent.getActivity(service, 0, notification_intent, 0)
            notification_builder.setContentTitle(title)
            notification_builder.setContentText(message)
            notification_builder.setContentIntent(intent)
            Drawable = jnius.autoclass("{}.R$drawable".format(service.getPackageName()))
            icon = getattr(Drawable, 'icon')
            notification_builder.setSmallIcon(icon)
            notification_builder.setAutoCancel(True)
            new_notification = notification_builder.getNotification()
            service.startForeground(1, new_notification)

    def start_service(self):
        if platform == 'android':
            from jnius import autoclass
            service = autoclass('ru.mrcpp.disposals.ServiceDisposals')
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            service.start(mActivity, '')


    def load_all_kv_files(self, directory_kv_files):
        for kv_file in os.listdir(directory_kv_files):
            kv_file = join(directory_kv_files, kv_file)
            if os.path.isfile(kv_file):
                if not PY2:
                    with open(kv_file, encoding='utf-8') as kv:
                        Builder.load_string(kv.read())
                else:
                    Builder.load_file(kv_file)

    def events_program(self, instance, keyboard, keycode, text, modifiers):

        if keyboard in (1001, 27):
            if self.nav_drawer.state == 'open':
                self.nav_drawer.toggle_nav_drawer()
            self.back_screen(event=keyboard)
        elif keyboard in (282, 319):
            pass

        return True

    def back_screen(self, event=None):

        if event in (1001, 27):
            if self.manager.current == 'base':
                self.dialog_exit()
                return
            try:
                self.manager.current = self.list_previous_screens.pop()
            except:
                self.manager.current = 'base'
            self.screen.ids.action_bar.title = self.translation._(self.title)
            self.screen.ids.action_bar.left_action_items = \
                [['menu', lambda x: self.nav_drawer._toggle()]]

    def show_about(self, *args):
        self.nav_drawer.toggle_nav_drawer()
        self.screen.ids.about.ids.label.text = \
            self.translation._(
                u'[size=20][b]Disposals[/b][/size]\n\n'
                u'[b]Version:[/b] {version}\n'
                u'[b]License:[/b] MIT\n\n'
                u'[size=20][b]Developer[/b][/size]\n\n'
                u'[ref=https://mrcpp.ru]'
                u'[color={link_color}]mrcpp[/color][/ref]\n\n'
                u'[b]Source code:[/b] '
                u'[ref=https://github.com/sidorovpp/Disposals]'
                u'[color={link_color}]GitHub[/color][/ref]').format(
                version=__version__,
                link_color=get_hex_from_color(self.theme_cls.primary_color)
            )
        self.manager.current = 'about'
        self.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen(27)]]

    def show_license(self, *args):
        if not PY2:
            self.screen.ids.license.ids.text_license.text = \
                self.translation._('%s') % open(
                    join(self.directory, 'LICENSE'), encoding='utf-8').read()
        else:
            self.screen.ids.license.ids.text_license.text = \
                self.translation._('%s') % open(
                    join(self.directory, 'LICENSE')).read()
        self.nav_drawer._toggle()
        self.manager.current = 'license'
        self.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen(27)]]
        self.screen.ids.action_bar.title = \
            self.translation._('Лицензия')

    def refresh_list(self, *args):
        if self.nav_drawer.state == 'open':
            self.nav_drawer._toggle()
        #self.screen.ids.base.ids.disposal_list.clear_widgets()
        self.screen.ids.base.ids.disposal_list.refresh_list()


    def show_settings(self, *args):
        self.nav_drawer._toggle()
        self.manager.current = 'settings_form'
        self.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen(27)]]
        self.screen.ids.action_bar.title = \
            self.translation._('Настройки')

    def filter_list(self, *args):

        def select_filter(filter):
            for key in self.filter_items.keys():
                if (filter == self.filter_items[key]) and (self.current_filter != key):
                    self.current_filter = key
                    self.config.set('General', 'filter', self.current_filter)
                    self.config.write()
                    self.window_filter.dismiss()
                    self.set_value_from_config()
                    self.refresh_list()

        dict_info_filters = {}
        for filter in self.filter_items:
            dict_info_filters[self.filter_items[filter]] = \
                ['filter', filter == self.current_filter]

        if not self.window_filter:
            self.window_filter = card(
                Lists(
                    dict_items=dict_info_filters,
                    events_callback=select_filter, flag='one_select_check'
                ),
                size=(.85, .55)
            )
        self.window_filter.open()

    def select_locale(self, *args):

        def select_locale(name_locale):

            for locale in self.dict_language.keys():
                if name_locale == self.dict_language[locale]:
                    self.lang = locale
                    self.config.set('General', 'language', self.lang)
                    self.config.write()
                    self.window_language.dismiss()
                    self.set_value_from_config()

        dict_info_locales = {}
        for locale in self.dict_language.keys():
            dict_info_locales[self.dict_language[locale]] = \
                ['locale', locale == self.lang]

        if not self.window_language:
            self.window_language = card(
                Lists(
                    dict_items=dict_info_locales,
                    events_callback=select_locale, flag='one_select_check'
                ),
                size=(.85, .55)
            )
        self.window_language.open()

    def dialog_exit(self):
        #Прячу приложение, при выходе выдаёт ошибку (пока не разобрался)
        if platform == 'android':
            from jnius import autoclass
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            activity.moveTaskToBack(True)
    #    def check_interval_press(interval):
    #        self.exit_interval += interval
    #        if self.exit_interval > 5:
    #            self.exit_interval = False
    #            Clock.unschedule(check_interval_press)
    #
    #   if self.exit_interval:
    #        self.stop()
    #
    #    Clock.schedule_interval(check_interval_press, 1)
    #
    #    toast(self.translation._('Нажмите еще раз для выхода'))

    def on_lang(self, instance, lang):
        self.translation.switch_lang(lang)

    def on_resume(self):
        # стартуем сервис уведомлений
        self.start_service()
