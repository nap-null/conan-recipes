import os
from conans import ConanFile, tools


class QtConan(ConanFile):
    name = "qt"
    version = "5.15.2"
    settings = "os", "arch", "compiler", "build_type"

    def source(self):
        git = tools.Git()
        git.clone('https://github.com/qt/qt5.git')
        git.checkout('v5.15.2')
        self.run('./init-repository')

    def build_configure(self):
        args = [
            '-prefix', self.package_folder,
            '-xplatform', self.xplatform,
            '-skip qtwebengine',
            '-opensource',
            '-confirm-license',
            '-nomake examples',
            '-nomake tests',
        ]

        if self.settings.build_type == 'Debug':
            args.append('-debug')
            args.append('-no-framework')
        else:
            args.append('-release')

        if self.settings.os == 'Android':
            if self.settings.arch:
                args.append('-android-arch')
                args.append('arm64-v8a' if self.settings.arch == 'armv8' else 'armeabi-v7a')
            else:
                args.append('-android-abis arm64-v8a,armeabi-v7a')
        else:
            args.append('-static')

        self.run(f"{self.source_folder}/configure {' '.join(args)}")

    def build_make(self):
        self.run('make -j6')
        self.run('make -j1 install')

    def build(self):
        open('.qmake.stash', 'w').close()
        open('.qmake.super', 'w').close()

        self.build_configure()
        self.build_make()

    def package(self):
        self.copy('*', src='package', dst='.', excludes='doc/*')

    def package_info(self):
        self.cpp_info.builddirs = [os.path.join(self.package_folder)]

    @property
    def xplatform(self):
        if self.settings.os == 'iOS':
            return 'macx-ios-clang'
        if self.settings.os == 'Android':
            return 'android-clang'
        return 'macx-clang'
