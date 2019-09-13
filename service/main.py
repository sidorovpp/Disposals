from time import sleep
from libs.uix.baseclass.disposalsdroid import connect_manager
from os.path import dirname
from os.path import join
from os.path import pardir
from os.path import realpath
from kivy.config import ConfigParser
from kivy.utils import platform
from common.utils import write_debug_log


#проверка непрочитанных задач и уведомление
def check_disposals(count):
    write_debug_log('check')
    res = connect_manager.GetResult('getDisposalList', {'readed': 0}, ['Number'])
    if (len(res) > 0) and (len(res) != count):
        from plyer import notification
        from plyer import vibrator

        title = 'Есть непрочитанные задачи'
        message = 'Непрочитанных задач:' + str(len(res))
        ticker = 'Уведомление'
        kwargs = {'title': title, 'message': message}
        kwargs['app_name'] = 'disposals'
        if platform == 'android':
            kwargs['app_icon'] = join(dirname(realpath(__file__)), 'notify.png')
        else:
            kwargs['app_icon'] = join(dirname(realpath(__file__)), 'notify.ico')
        kwargs['ticker'] = ticker
        #вибрируем
        if platform == 'android':
            vibrator.vibrate(1)
            sleep(1)
            vibrator.cancel()

        #показываем уведомление
        notification.notify(**kwargs)

    return len(res)

def start_foreground():
    import jnius
    Context = jnius.autoclass('android.content.Context')
    Intent = jnius.autoclass('android.content.Intent')
    PendingIntent = jnius.autoclass('android.app.PendingIntent')
    AndroidString = jnius.autoclass('java.lang.String')
    NotificationBuilder = jnius.autoclass('android.app.Notification$Builder')
    # Notification = jnius.autoclass('android.app.Notification')
    # service_name = 'S1'
    # package_name = 'com.something'
    service = jnius.autoclass('org.kivy.android.PythonService').mService
    # Previous version of Kivy had a reference to the service like below.
    # service = jnius.autoclass('{}.Service{}'.format(package_name, service_name)).mService
    PythonActivity = jnius.autoclass('org.kivy.android' + '.PythonActivity')
    notification_service = service.getSystemService(
        Context.NOTIFICATION_SERVICE)
    app_context = service.getApplication().getApplicationContext()
    notification_builder = NotificationBuilder(app_context)
    title = AndroidString("EzTunes".encode('utf-8'))
    message = AndroidString("Ready to play music.".encode('utf-8'))
    # app_class = service.getApplication().getClass()
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
    # Below sends the notification to the notification bar; nice but not a foreground service.
    # notification_service.notify(0, new_noti)
    service.startForeground(1, new_notification)


if __name__ == '__main__':
    try:
        write_debug_log('start')
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

        #write_debug_log('connect')
        #инициализируем соединение
        start_foreground()
        try:
            connect_manager.InitConnect()
        except:
            pass

        count = 0
        while True:
            #write_debug_log('cycle')
            sleep(30)
            count = check_disposals(count)


    except Exception as E:
        if platform == 'android':
            # пишу в папку на карту ошибку (андроид)
            f = '/sdcard/disposals/service_error.log'
        else:
            f = join(dirname(realpath(__file__)), pardir,  'service_error.log')
        with open(f, 'w+') as f:
                f.write(str(E))

