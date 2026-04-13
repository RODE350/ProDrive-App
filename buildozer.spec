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

# 🔥 Versions stables Android
requirements = python3, kivy==2.3.1, kivymd==1.1.1, pillow
orientation = portrait

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Architectures
android.archs = arm64-v8a, armeabi-v7a

# 🔥 Compatibilité Android moderne
android.api = 33
android.minapi = 21

# Stockage
android.private_storage = True
android.allow_backup = True

# APK debug
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
