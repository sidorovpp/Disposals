from time import sleep
from libs.uix.baseclass.disposalsdroid import connect_manager
from os.path import dirname
from os.path import join
from os.path import pardir
from os.path import realpath
from kivy.config import ConfigParser
from kivy.utils import platform
from plyer import notification
from plyer import storagepath
import traceback

#проверка непрочитанных задач и уведомление
def check_disposals(count, first):
    #write_debug_log('check')
    print('Service check starting...')
    try:
        res = connect_manager.GetResult('getDisposalList', {'readed': 0}, ['Number'])
    except:
        print('Service connection error')
        return 0

    if len(res) > 0:
        title = 'Есть непрочитанные задачи'
        message = 'Непрочитанных задач:' + str(len(res))
    else:
        title = 'Нет непрочитанных задач'
        message = 'Все задачи прочитаны'

    ticker = 'Уведомление'

    kwargs = {'title': title, 'message': message, 'ticker': ticker, 'app_name': 'Disposals'}
    if platform == "win":
        kwargs['app_icon'] = join(dirname(realpath(__file__)),
                                  'notify.ico')
        kwargs['timeout'] = 4
    else:
        kwargs['app_icon'] = join(dirname(realpath(__file__)),
                                  'notify.png')
    notification.notify(**kwargs)
    return len(res)

def show_notification(title, message):
    import jnius

    #stop_foreground()

    Context = jnius.autoclass('android.content.Context')
    Intent = jnius.autoclass('android.content.Intent')
    PendingIntent = jnius.autoclass('android.app.PendingIntent')
    AndroidString = jnius.autoclass('java.lang.String')
    NotificationBuilder = jnius.autoclass('android.app.Notification$Builder')
    service = jnius.autoclass('org.kivy.android.PythonService').mService
    PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
    notification_service = service.getSystemService(
        Context.NOTIFICATION_SERVICE)
    app_context = service.getApplication().getApplicationContext()

    #создаём channel
    from plyer.platforms.android import SDK_INT
    if SDK_INT > 26:
        manager = jnius.autoclass('android.app.NotificationManager')
        channel = jnius.autoclass('android.app.NotificationChannel')

        app_channel = channel(service.getPackageName(), title, manager.IMPORTANCE_DEFAULT)
        service.getSystemService(manager).createNotificationChannel(app_channel)
        notification_builder = NotificationBuilder(app_context, service.getPackageName())
    else:
        notification_builder = NotificationBuilder(app_context)

    title = AndroidString(title.encode('utf-8'))
    message = AndroidString(message.encode('utf-8'))
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
    #icon = getattr(Drawable, 'icon')
    icon = getattr(Drawable, 'presplash')
    notification_builder.setSmallIcon(icon)
    notification_builder.setAutoCancel(True)
    new_notification = notification_builder.getNotification()
    service.startForeground(1, new_notification)

def set_autorestart():
    from jnius import autoclass
    PythonService = autoclass('org.kivy.android.PythonService')
    PythonService.mService.setAutoRestartService(True)

def stop_foreground():
    from jnius import autoclass
    Service = autoclass('org.renpy.android.PythonService').mService
    Service.stopForeground(True)


if __name__ == '__main__':
    try:
        #write_debug_log('start')
        config = ConfigParser()
        config.read(join(dirname(realpath(__file__)), pardir,  'disposals.ini'))
        connect_manager.server = config.get('General', 'ip')
        connect_manager.username = config.get('General', 'user')
        connect_manager.password = config.get('General', 'password')
        connect_manager.sms = config.get('General', 'sms')

        #системные настройки
        config.read(join(dirname(realpath(__file__)), pardir,  'server_.ini'))
        connect_manager.sysusername = config.get('Access', 'user')
        connect_manager.syspassword = config.get('Access', 'password')

        #write_debug_log('connect')
        #инициализируем соединение
        #set_autorestart()
        try:
            connect_manager.InitConnect()
        except:
            pass

        count = check_disposals(0, True)
        while True:
            sleep(120)
            count = check_disposals(count, False)

    except Exception as E:
        print('Service error:')
        text_error = traceback.format_exc()
        print(text_error)
        f = join(storagepath.get_downloads_dir(), 'service_error.log)')
        with open(f, 'w+') as f:
                f.write(str(E))

