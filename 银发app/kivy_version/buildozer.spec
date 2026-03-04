[app]

title = 银发关爱
package.name = silverhair
package.domain = org.silverhair

source.dir = .
source.include_exts = py,png,jpg,kv,db,json,mp3,wav

version = 1.0.0

requirements = python3,kivy,pyttsx3,requests,comtypes,pyjnius,android

fullscreen = 0
orientation = portrait

android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,RECORD_AUDIO,CALL_PHONE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 30
android.minapi = 21
android.ndk = 21b
android.sdk = 30

android.archs = arm64-v8a,armeabi-v7a

[buildozer]

log_level = 2

[android]

presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png
