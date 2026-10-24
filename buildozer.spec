[app]
title = RR Marim Elétrica
package.name = rrmarimeletrica
package.domain = br.com.rrmarim
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf
version = 1.0.0
requirements = python3,kivy,fpdf2,pillow
orientation = portrait
fullscreen = 0
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.allow_backup = True
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
