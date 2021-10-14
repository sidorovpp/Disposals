[app]

# (str) Title of your application
title = Disposals

# (str) Package name
package.name = disposals

# (str) Package domain (needed for android/ios packaging)
package.domain = ru.mrcpp

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ini,po,mo,rst,txt,wav,aar

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin

# (list) List of exclusions using pattern matching
source.exclude_patterns = disposals.ini

# (str) Application versioning (method 1)
version = 0.1

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma seperated e.g. requirements = sqlite3,kivy
requirements =  python3,kivy==2.0.0rc4,https://github.com/kivymd/KivyMD/archive/master.zip,pygments,sdl2_ttf==2.0.15,pillow, pyjnius, jnius, git+https://github.com/kivy/plyer@master#egg=plyer

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
presplash.filename = %(source.dir)s/data/wait.png

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (list) List of service to declare
services = Disposals:./service/main.py:sticky

#
# OSX Specific
#

#
# author = © Copyright Info

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for new android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
android.presplash_color = #003380

# (list) Permissions
android.permissions = INTERNET, VIBRATE, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, FOREGROUND_SERVICE, ACCESS_FINE_LOCATION

# (int) Target Android API, should be as high as possible.
android.api = 28
# (int) Minimum API your APK will support.
android.minapi = 21
# (str) Android NDK version to use
android.ndk = 19b

android.add_aars = ./libs/support-v4-24.1.1.aar

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = False

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
android.skip_update = False
# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True
# (str) Android logcat filters to use
# android.logcat_filters = *:S python:D
# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = armeabi-v7a

#добавил для Notifications
p4a.branch = develop

# (list) Gradle dependencies to add
android.gradle_dependencies = androidx.work:work-runtime:2.2.0

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an 'androidx' package, or any package from Kotlin source.
# android.enable_androidx requires android.api >= 28
android.enable_androidx = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0
# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer
# (str) Path to build output (i.e. .apk, .ipa) storage
bin_dir = ./bin