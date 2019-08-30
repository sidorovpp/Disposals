# список задач
from libs.uix.baseclass.disposalsdroid import connect_manager
from kivymd.button import MDFlatButton
from kivy.app import App
from kivymd.label import MDLabel
from kivymd.dialog import MDDialog
from kivy.metrics import dp
import threading
from kivy.clock import Clock, mainthread
from kivy.uix.recycleview import RecycleView
from datetime import datetime
from libs.uix.baseclass.utils import show_dialog
from kivy.utils import get_hex_from_color
from ast import literal_eval
from libs.applibs.toast import toast
from kivy.utils import platform

class NumberLabel(MDLabel):
    def on_ref_press(self, url):
        app = App.get_running_app()
        app.screen.ids.base.disposal_list.refresh_list(literal_eval('{' + url + '}'))
        button = self.parent.parent

        #отключаем прорисовку нажатия кнопки при клике на ссылку
        button.fade_bg.stop_property(button, '_current_button_color')
        return super(MDLabel, self).on_ref_press(url)


class DisposalItem(MDFlatButton):

    _data = []

    def get_data(self):
        return self._data

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)

        self.app = App.get_running_app()


    def set_data(self, val):
        #конвертация даты
        def get_date(str):
            #ищу разделитель между цифрами, менялся с . на -
            if str.find('-') >= 0:
                d = '-'
            else:
                d = '.'
            #что сначала - год?
            if str.find(d) == 4:
                fmt = '%Y' + d + '%m' + d + '%d %H:%M:%S'
            else:
                fmt = '%d' + d +'%m' + d +'%Y %H:%M:%S'
            if len(str) > 10:
                return datetime.strptime(str, fmt)
            else:
                return datetime.strptime(str, fmt[:8])

        #Фамилия И.О.
        def get_staff_short(s):
            k = s.find(' ')
            k1 = s.find(' ', k + 1)
            return s[:k + 1] + s[k + 1] + '.' + s[k1 + 1] + '.'

        self._data = val
        # номер
        self.number_label.text = r'[color=#003380]#{number}[/color] ([ref="sender_id":{sender_id}][color={link_color}][u]{sender}[/u][/color][/ref]' \
                                 r'=> [ref="receiver_id":{receiver_id}][color={link_color}][u]{receiver}[/u][/color][/ref])'.format(
                number=self.data['Number'],
                sender=get_staff_short(self.data['Sender']),
                receiver=get_staff_short(self.data['Receiver']),
                sender_id=self.data['Sender_id'],
                receiver_id=self.data['Receiver_id'],
                link_color=get_hex_from_color(self.app.theme_cls.primary_color))

        # тема
        theme = self.data['Theme']
        theme = theme.replace('\n', ' ')
        text = self.data['Task'].replace('\n', ' ')
        self.theme_label.text = '{0}'.format(theme)
        self.text_label.text = '{0}'.format(text)
        # иконка и цвет выполнения
        if self.data['IsComplete'] == '0':
            if (self.data['PlanDateTo'] != '') and (datetime.now() > get_date(self.data['PlanDateTo'])):
                self.icon.text_color = [1, 0, 0, 1]
            else:
                self.icon.text_color = [0, 0, 0, 1]
            self.icon.icon_text = 'clock'
        else:
            self.icon.icon_text = 'calendar-check'
            if self.data['IsConfirmed'] != '':
                self.icon.text_color = [0, 0, 1, 1]
            else:
                self.icon.text_color = [0, 1, 0, 1]

        if self.data['IsReaded'] == '0':
            self.theme_label.text = '[b]{0}[/b]'.format(self.theme_label.text)
            self.text_label.text = '[b]{0}[/b]'.format(self.text_label.text)
        # иконка и шрифт отклонения
        if self.data['IsDisallowed'] == '1':
            self.icon.icon_text = 'stop'

    data = property(get_data, set_data)

    def set_readed(self):
        try:
            number = self.app.screen.ids.disposal.number.text
            connect_manager.GetResult('SetTaskRead', {'id': int(number)}, [])
        except:
            pass

    def execute(self):
        def _execute(dialog):
            try:
                number = self.app.screen.ids.disposal.number.text
                connect_manager.GetResult('ExecuteDisposal', {'disposal_id': int(number)}, [])
                dialog.dismiss()
            except:
                pass

        show_dialog(self.app.translation._('Вопрос'),
                       self.app.translation._('Выполнить задачу?'),
                       _execute)

    def set_disposal_params(self, item_data):
        self.app.screen.ids.disposal.set_params(item_data)

    # ищем следующий элемент
    def show_next(self):
        number = self.app.screen.ids.disposal.number.text

        for i in self.parent.parent.data:
            if i['data']['Number'] < number:
                self.set_disposal_params(i['data'])
                break

    # ищем предыдущий элемент
    def show_prior(self):
        number = self.app.screen.ids.disposal.number.text

        for i in self.parent.parent.data[::-1]:
            if i['data']['Number'] > number:
                self.set_disposal_params(i['data'])
                break

    def on_release(self):
        # считываем отправителя, получателя и добавляем к data
        self.set_disposal_params(self.data)
        self.app.manager.current = 'disposal'
        self.app.screen.ids.action_bar.title = self.app.translation._('Задача')

        # добавляем кнопки следующая, предыдущая, назад и прочитано
        self.app.screen.ids.action_bar.left_action_items = [['chevron-left', lambda x: self.app.back_screen(27)]]
        self.app.screen.ids.action_bar.right_action_items = [['read', lambda x: self.set_readed()],
                                                             ['checkbox-marked-circle', lambda x: self.execute()],
                                                             ['skip-previous', lambda x: self.show_prior()],
                                                             ['skip-next', lambda x: self.show_next()]]


def get_number(i):
    return i[0]


class DisposalList(RecycleView):

    Receivers = []

    def __init__(self, *args, **kwargs):
        super(DisposalList, self).__init__(*args, **kwargs)
        self.app = App.get_running_app()

    def start_spinner(self, *args):
        self.app.screen.ids.base.spinner.active = True

    @mainthread
    def stop_spinner(self, *args):
        self.app.screen.ids.base.spinner.active = False

    @mainthread
    def make_list(self, res):
        self.data = []

        for i in res:
            item = dict({'Number': i[0],
                        'Theme': i[1],
                        'Task': i[5],
                        'ShortTask': i[2],
                        'Receiver_id': i[4],
                        'Sender_id': i[3],
                        'IsComplete': i[6],
                        'IsDisallowed': i[8],
                        'IsReaded': i[7],
                        'PlanDateTo': i[9],
                        'Sender': i[11],
                        'Receiver': i[12],
                        'IsConfirmed': i[10]
                        })

            self.data.append({'data': item,'height': dp(70)})

        self.stop_spinner()
        if platform == 'android':
            toast(self.app.translation._('Загружено задач:') + ' ' + str(len(res)))

    def on_scroll_stop(self, touch, check_children=True):
        super(DisposalList, self).on_scroll_stop(touch, check_children=True)
        if self.scroll_y > 1:
            self.refresh_list(params={})

    @mainthread
    def show_connect_error(self):
        self.stop_spinner()
        content = MDLabel(
            font_style='Body1',
            text=self.app.translation._('Нет подключения, проверьте настройки!'),
            size_hint_y=None,
            valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title=self.app.translation._('Внимание'),
                               content=content,
                               size_hint=(.8, None),
                               height=dp(200))

        self.dialog.add_action_button("ОК",
                                      action=lambda *x: self.dialog.dismiss())
        self.dialog.open()

    # загрузка списка
    def load_data(self, params):

        def get_staff(staff_list, id ):
            for i in staff_list:
                if i[0] == id:
                    return i[1]
            return ''

        Clock.schedule_once(self.start_spinner, 0)
        try:
            #если не заполнен текущий пользователь - получаем
            if connect_manager.StaffID == None:
                connect_manager.StaffID = connect_manager.GetResult('getStaffID', {}, [])

            Columns = ['Number', 'Theme', 'ShortTask', 'Sender_id', 'Receiver_id', 'Task', 'isExecute', 'Readed', 'Disabled', 'PlanDateTo', 'IsConfirmed']
            search = self.app.screen.ids.base.number_search.text.strip()
            if search != '' and len(search) > 2:
                search = search.replace('%', '!%')
                if search.isnumeric():
                    #ищем по номеру
                    params.update({'Number': '%%' + search + '%%'})
                    res = connect_manager.GetResult('getDisposalList', params, Columns)
                else:
                    #ищем по теме или тексту
                    params2 = params.copy()
                    params.update({'zadanie': '%%' + search + '%%'})
                    params2.update({'Theme': '%%' + search + '%%'})
                    res = connect_manager.GetResult('getDisposalList', params, Columns)
                    res += connect_manager.GetResult('getDisposalList', params2, Columns)
                    #убираем дубли
                    unique_list = []
                    [unique_list.append(obj) for obj in res if obj not in unique_list]
                    res = unique_list
            elif self.app.current_filter == 'NotReaded':
                params.update({'readed': 0})
                res = connect_manager.GetResult('getDisposalList', params, Columns)
            elif self.app.current_filter == 'FromMe':
                params.update({'isExecute': 0, 'Sender_id': connect_manager.StaffID})
                res = connect_manager.GetResult('getDisposalList', params, Columns)
            elif self.app.current_filter == 'ToMe':
                params.update({'isExecute': 0, 'Receiver_id': connect_manager.StaffID})
                res = connect_manager.GetResult('getDisposalList', params, Columns)
            else:
                params.update({'isExecute': 0})
                res = connect_manager.GetResult('getDisposalList', params, Columns)
                # res = GetResult('getDisposalList', {'isExecute': 0, 'Receiver_id': 43},
                #                  ['Number', 'Theme', 'ShortTask', 'Sender_id', 'Receiver_id', 'Task', 'isExecute', 'Readed',
                #                   'Disabled'])

            res = sorted(res, key=get_number, reverse=True)

            if len(res) > 0:
                #загружаем отправителей и получателей
                ids = set()
                for i in res:
                    ids.add(i[3])
                    ids.add(i[4])

                staff = connect_manager.GetResult('getStaff', {'id': list(ids)}, ['_id', 'userName'])

                #прописываем отправителей и получателей
                for i in res:
                    i.append(get_staff(staff, i[3]))
                    i.append(get_staff(staff, i[4]))

            # формируем список
            self.make_list(res)
        except Exception as error:
            print(error)
            # сообщение об ошибке
            self.show_connect_error()

    # обновление списка задач
    def refresh_list(self, params):
        mythread = threading.Thread(target=self.load_data,  kwargs = {'params':params})
        mythread.start()


