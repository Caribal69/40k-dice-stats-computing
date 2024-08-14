[app]

title = Test App
package.name = testapp
package.domain = org.test.appname

# (list) Source files to include (let's include everything in the src directory)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,csv

version = 0.1
requirements = python3,kivy,kivy-md,numpy,pandas

# (str) python-for-android branch to use, defaults to master
p4a.branch = master

# (list) List of inclusions using pattern matching
source.include_patterns = src/*, data/*

orientation = portrait
fullscreen = 0

# TEST
# ---------
# (int) Android API to use
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 23b

# ---------













# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = armeabi-v7a

# change the major version of python used by the app
osx.python_version = 3
# Kivy version to use
osx.kivy_version = 1.9.1

# iOS specific
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.7.0

[buildozer]
log_level = 3
# log_level = 2  # debug