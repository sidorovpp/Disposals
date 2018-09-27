from time import sleep
from libs.uix.baseclass.disposalsdroid import GetResult
from os.path import dirname
from os.path import join
from os.path import pardir
from os.path import realpath
from kivy.config import ConfigParser
import libs.uix.baseclass.disposalsdroid as DisposalsDroid
import traceback
from shutil import copyfile

#проверка непрочитанных задач и уведомление
def check_disposals():
    res = GetResult('getDisposalList', {'readed': 0}, ['Number'])
    if len(res) > 0:
        from plyer import notification
        from plyer import vibrator
        from plyer.utils import platform

        title = 'Есть непрочитанные задачи'
        message = 'Непрочитанных задач:' + str(len(res))
        ticker = 'Уведомление'
        kwargs = {'title': title, 'message': message}
        kwargs['app_name'] = 'disposals'
        if platform == "win":
            kwargs['app_icon'] = join(dirname(realpath(__file__)), 'notify.ico')
            kwargs['timeout'] = 4
        else:
            kwargs['app_icon'] = join(dirname(realpath(__file__)), 'notify.png')
            kwargs['ticker'] = ticker
        #вибрация
        vibrator.vibrate(0.5)
        #показываем уведомление
        notification.notify(**kwargs)


if __name__ == '__main__':
    try:
        config = ConfigParser()
        config.read(join(dirname(realpath(__file__)), pardir,  'disposals.ini'))
        DisposalsDroid.server = config.get('General', 'ip')
        DisposalsDroid.username = config.get('General', 'user')
        DisposalsDroid.password = config.get('General', 'password')

        while True:
            sleep(60)
            check_disposals()


    except Exception as E:
        with open('/sdcard/disposals/service_error.log', 'w+') as f:
            f.write(str(E))
