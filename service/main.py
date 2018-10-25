from time import sleep
from libs.uix.baseclass.disposalsdroid import connect_manager
from os.path import dirname
from os.path import join
from os.path import pardir
from os.path import realpath
from kivy.config import ConfigParser

#проверка непрочитанных задач и уведомление
def check_disposals():
    res = connect_manager.GetResult('getDisposalList', {'readed': 0}, ['Number'])
    if len(res) > 0:
        from plyer import notification
        from plyer import vibrator

        title = 'Есть непрочитанные задачи'
        message = 'Непрочитанных задач:' + str(len(res))
        ticker = 'Уведомление'
        kwargs = {'title': title, 'message': message}
        kwargs['app_name'] = 'disposals'
        kwargs['app_icon'] = join(dirname(realpath(__file__)), 'notify.png')
        kwargs['ticker'] = ticker
        #показываем уведомление
        notification.notify(**kwargs)


if __name__ == '__main__':
    try:
        config = ConfigParser()
        config.read(join(dirname(realpath(__file__)), pardir,  'disposals.ini'))
        connect_manager.server = config.get('General', 'ip')
        connect_manager.username = config.get('General', 'user')
        connect_manager.password = config.get('General', 'password')
        connect_manager.sms = config.get('General', 'sms')

        #системные настройки
        config.read(join(dirname(realpath(__file__)), pardir,  'server.ini'))
        connect_manager.sysusername = config.get('Access', 'user')
        connect_manager.syspassword = config.get('Access', 'password')

        #инициализируем соединение
        try:
            connect_manager.InitConnect()
        except:
            pass

        while True:
            sleep(180)
            check_disposals()


    except Exception as E:
        #пишу в папку на карту ошибку (андроид)
        with open('/sdcard/disposals/service_error.log', 'w+') as f:
            f.write(str(E))
