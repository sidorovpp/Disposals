from time import sleep
from libs.uix.baseclass.disposalsdroid import connect_manager
from os.path import dirname
from os.path import join
from os.path import pardir
from os.path import realpath
from kivy.config import ConfigParser
from kivy.utils import platform
from plyer import notification
from plyer import vibrator
from kivy.core.audio import SoundLoader
import traceback
from common.utils import write_debug_log



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
        if (len(res) != count) or first:
            if len(res) > 0:
                id = res[0][0]
            else:
                id = '0'
            show_notification_new(title, message, id)
            if (len(res) > 0):
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

def show_notification_new(title, text, notification_id):
    from jnius import autoclass, cast
    from android import python_act

    # Gets the current running instance of the app so as to speak
    mActivity = autoclass("org.kivy.android.PythonActivity").mActivity
    write_debug_log('mActivity = autoclass("org.kivy.android.PythonActivity").mActivity')
    context = mActivity.getApplicationContext()
    write_debug_log('context = mActivity.getApplicationContext()')

    # Autoclass necessary java classes so they can be used in python
    RingtoneManager = autoclass("android.media.RingtoneManager")
    write_debug_log('RingtoneManager = autoclass("android.media.RingtoneManager")')
    Uri = autoclass("android.net.Uri")
    write_debug_log('Uri = autoclass("android.net.Uri")')
    AudioAttributesBuilder = autoclass("android.media.AudioAttributes$Builder")
    write_debug_log('AudioAttributesBuilder = autoclass("android.media.AudioAttributes$Builder")')
    AudioAttributes = autoclass("android.media.AudioAttributes")
    write_debug_log('AudioAttributes = autoclass("android.media.AudioAttributes")')
    AndroidString = autoclass("java.lang.String")
    write_debug_log('AndroidString = autoclass("java.lang.String")')
    NotificationManager = autoclass("android.app.NotificationManager")
    write_debug_log('NotificationManager = autoclass("android.app.NotificationManager")')
    NotificationChannel = autoclass("android.app.NotificationChannel")
    write_debug_log('NotificationChannel = autoclass("android.app.NotificationChannel")')
    NotificationCompat = autoclass("androidx.core.app.NotificationCompat")
    write_debug_log('NotificationCompat = autoclass("androidx.core.app.NotificationCompat")')
    NotificationCompatBuilder = autoclass("androidx.core.app.NotificationCompat$Builder")
    write_debug_log('NotificationCompatBuilder = autoclass("androidx.core.app.NotificationCompat$Builder")')
    NotificationManagerCompat = autoclass("androidx.core.app.NotificationManagerCompat")
    write_debug_log('NotificationManagerCompat = autoclass("androidx.core.app.NotificationManagerCompat")')
    func_from = getattr(NotificationManagerCompat, "from")
    write_debug_log('func_from = getattr(NotificationManagerCompat, "from")')
    Intent = autoclass("android.content.Intent")
    write_debug_log('Intent = autoclass("android.content.Intent")')
    PendingIntent = autoclass("android.app.PendingIntent")
    write_debug_log('PendingIntent = autoclass("android.app.PendingIntent")')

    # create an object that represents the sound type of the notification
    sound = cast(Uri, RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION))
    att = AudioAttributesBuilder()
    att.setUsage(AudioAttributes.USAGE_NOTIFICATION)
    att.setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
    att = cast(AudioAttributes, att.build())

    # Name of the notification channel
    name = cast("java.lang.CharSequence", AndroidString(title))
    # Description for the notification channel
    description = AndroidString('Непрочитанные задачи')
    # Unique id for a notification channel. Is used to send notification through
    # this channel
    channel_id = AndroidString("disposals")

    # Importance level of the channel
    importance = NotificationManager.IMPORTANCE_HIGH
    # Create Notification Channel
    channel = NotificationChannel(channel_id, name, importance)
    channel.setDescription(description)
    channel.enableLights(True)
    channel.enableVibration(True)
    channel.setSound(sound, att)
    # Get android's notification manager
    notificationManager = context.getSystemService(NotificationManager)
    # Register the notification channel
    notificationManager.createNotificationChannel(channel)

    # Set notification sound
    sound = cast(Uri, RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION))
    # Create the notification builder object
    builder = NotificationCompatBuilder(context, AndroidString("disposals"))
    # Sets the small icon of the notification
    builder.setSmallIcon(context.getApplicationInfo().icon)
    # Sets the title of the notification
    builder.setContentTitle(
        cast("java.lang.CharSequence", AndroidString(title))
    )
    # Set text of notification
    builder.setContentText(
        cast("java.lang.CharSequence", AndroidString(text))
    )
    # Set sound
    builder.setSound(sound)
    # Set priority level of notification
    builder.setPriority(NotificationCompat.PRIORITY_HIGH)
    # If notification is visble to all users on lockscreen
    builder.setVisibility(NotificationCompat.VISIBILITY_PUBLIC)

    # code to make notification clickable
    # Create an intent
    intent = Intent(context, python_act)
    # Set some more data for the intent
    intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
    # Sets intent action type
    intent.setAction(Intent.ACTION_MAIN)
    # Set intent category type
    intent.addCategory(Intent.CATEGORY_LAUNCHER)

    # Create a pending Intent using your own unique id (int) value
    pending_intent = PendingIntent.getActivity(context, id, intent, 0)
    # Add pendingintent to notification
    notification.setContentIntent(pending_intent)
    # Auto dismiss the notification on press
    notification.setAutoCancel(True)

    # Create a notificationcompat manager object to add the new notification
    compatmanager = NotificationManagerCompat.func_from(context)
    # Pass an unique notification_id. This can be used to access the notification
    compatmanager.notify(notification_id, builder.build())

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

        count = check_disposals(0, True)
        while True:
            sleep(300)
            count = check_disposals(count, False)

    except Exception as E:
        print('Service error:')
        text_error = traceback.format_exc()
        print(text_error)
        if platform == 'android':
            # пишу в папку на карту ошибку (андроид)
            f = '/sdcard/disposals/service_error.log'
        else:
            f = join(dirname(realpath(__file__)), pardir,  'service_error.log')
        with open(f, 'w+') as f:
                f.write(str(E))

