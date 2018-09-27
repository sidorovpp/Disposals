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

def check_disposals():
    from plyer import notification
    from plyer.utils import platform

    res = GetResult('getDisposalList', {'readed': 0}, ['Number'])
    if len(res) > 0:
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
        notification.notify(**kwargs)


if __name__ == '__main__':
    config = ConfigParser()
    while True:
        config.read(join(dirname(realpath(__file__)), pardir,  'disposals.ini'))
        DisposalsDroid.server = config.get('General', 'ip')
        DisposalsDroid.username = config.get('General', 'user')
        DisposalsDroid.password = config.get('General', 'password')

        sleep(60)
        try:
            check_disposals()
        except:
            traceback.print_exc(file=open(join(dirname(realpath(__file__)), pardir,   'error.log'), 'w'))
            copyfile(join(app.directory, 'error.log'),
                     join('/sdcard', 'disposals', 'error.log')
                     )
