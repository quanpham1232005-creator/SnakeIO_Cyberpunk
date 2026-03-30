[app]
title = SnakeIO Cyberpunk
package.name = snakeio_cyberpunk
package.domain = org.test
source.dir = src
source.include_exts = py,png,jpg,kv,atlas,wav,mp3,json
version = 1.0.0
requirements = python3,pygame,asyncio

# Orientation (portrait, landscape or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use the Python-for-Android toolchain
p4a.branch = master

# (list) List of service to declare
services = 

# (str) Screen orientation
android.orientation = portrait

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) Allow backup
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
