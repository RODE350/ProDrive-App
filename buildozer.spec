[app]
title = ProDrive
package.name = prodrive
package.domain = org.prodrive
source.dir = .

# 🔥 IMPORTANT
source.include_exts = py,kv,png,jpg,jpeg,atlas,db,pdf
source.include_patterns = assets/*,images/*,database/*,*.db,*.pdf
version = 0.1

# 🔥 ICÔNE ET ÉCRAN DE DÉMARRAGE
icon.filename = logo1.png
presplash.filename = logo1.png

# 🔥 Requirements (Kivy 2.3.0 est plus stable pour le build auto)
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, reportlab

orientation = portrait
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.archs = arm64-v8a, armeabi-v7a

# 🔥 FIX POUR GITHUB ACTIONS
android.api = 31
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# Stockage
android.private_storage = True
android.allow_backup = True
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
