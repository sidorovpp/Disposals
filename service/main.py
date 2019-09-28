from time import sleep
from libs.uix.baseclass.disposalsdroid import connect_manager
from os.path import dirname
from os.path import join
from os.path import pardir
from os.path import realpath
from kivy.config import ConfigParser
from kivy.utils import platform
from common.utils import write_debug_log
from plyer import notification
from plyer import vibrator
from kivy.core.audio import SoundLoader


#проверка непрочитанных задач и уведомление
def check_disposals(count):
    #write_debug_log('check')
    res = connect_manager.GetResult('getDisposalList', {'readed': 0}, ['Number'])

    title = 'Есть непрочитанные задачи'
    message = 'Непрочитанных задач:' + str(len(res))
    ticker = 'Уведомление'
    kwargs = {'title': title, 'message': message}
    kwargs['app_name'] = 'disposals'

    if platform != 'android':
        if (len(res) != count):
            kwargs['app_icon'] = join(dirname(realpath(__file__)), 'notify.ico')
            kwargs['ticker'] = ticker

            #показываем уведомление
            notification.notify(**kwargs)
            # звук
            play_sound()
    else:
        show_notification(title, message)
        if (len(res) > 0) and (len(res) != count):
            from jnius import autoclass
            AudioManager = autoclass('android.media.AudioManager')
            Context = autoclass('android.content.Context')
            service = autoclass('org.kivy.android.PythonService').mService
            audioManager = service.getSystemService(Context.AUDIO_SERVICE)
            # проверяем режим телефона
            if audioManager.getRingerMode() == AudioManager.RINGER_MODE_NORMAL:
                #звук
                play_sound()
            elif audioManager.getRingerMode() == AudioManager.RINGER_MODE_VIBRATE:
                # вибрируем
                vibrator.vibrate(1)
                sleep(1)
                vibrator.cancel()

    return len(res)

def play_sound():
    if platform != 'android':
        #не везде работает (win 7 не сработало)
        try:
            sound = SoundLoader.load('new.wav')
            if sound:
                sound.play()
        except:
            pass
    else:
        from jnius import autoclass

        # MediaPlayer
        MediaPlayer = autoclass('android.media.MediaPlayer')

        # проигрываем звук
        mPlayer = MediaPlayer()
        mPlayer.setDataSource(join(dirname(realpath(__file__)), 'new.wav'))
        mPlayer.prepare()
        duration = mPlayer.getDuration()
        mPlayer.start()
        sleep(int(duration + 1))
        mPlayer.release()

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
    icon = getattr(Drawable, 'icon')
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
        config.read(join(dirname(realpath(__file__)), pardir,  'server.ini'))
        connect_manager.sysusername = config.get('Access', 'user')
        connect_manager.syspassword = config.get('Access', 'password')

        #write_debug_log('connect')
        #инициализируем соединение
        #set_autorestart()
        try:
            connect_manager.InitConnect()
        except:
            pass

        count = check_disposals(0)
        while True:
            #write_debug_log('cycle')
            sleep(300)
            count = check_disposals(count)


    except Exception as E:
        if platform == 'android':
            # пишу в папку на карту ошибку (андроид)
            f = '/sdcard/disposals/service_error.log'
        else:
            f = join(dirname(realpath(__file__)), pardir,  'service_error.log')
        with open(f, 'w+') as f:
                f.write(str(E))

