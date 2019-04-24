from datetime import datetime
from os.path import dirname
from os.path import join
from os.path import pardir
from os.path import realpath
from kivy.utils import platform


def write_debug_log(text):
    if platform == 'android':
        # пишу в папку на карту ошибку (андроид)
        f = '/sdcard/disposals/debug.log'
    else:
        f = join(dirname(realpath(__file__)), pardir, 'debug.log')
    with open(f, 'a+') as f:
        f.write(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S : "))
        f.write(text + '\n')
