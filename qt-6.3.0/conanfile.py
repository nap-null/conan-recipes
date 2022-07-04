import os
from conans import ConanFile, CMake, VisualStudioBuildEnvironment, tools
from conan.tools.microsoft import is_msvc
import pprint


class QtConan(ConanFile):
    name = "qt"
    version = "6.3.0"
    settings = "os", "arch", "compiler", "build_type"

    exports = [ "patches/*.diff" ]
    patches = [ ]

    no_copy_source = True

    def build_requirements(self):
        if self.settings.os == 'iOS':
            self.build_requires("qt/6.3.0")

    def source(self):
        git = tools.Git(folder='qt5')
        git.clone('https://github.com/qt/qt5.git')
        git.checkout('v' + self.version)

        with tools.chdir('qt5'):
            self.run('perl init-repository')

            for patch in self.patches:
                print(f"Applying patch '{patch}'...")
                self.run(f'git apply ../patches/{patch}')

            self.run('rm -rf qtwebglplugin qtvirtualkeyboard qtgamepad')

    def build_configure(self):

        args = [
            '-prefix', os.path.join(self.build_folder, 'package'),
            '-skip qtwebengine',
            '-opensource',
            '-confirm-license',
            '-nomake examples',
            '-nomake tests',
        ]

        if self.xplatform:
            args.append('-xplatform')
            args.append(self.xplatform)

        if self.settings.build_type == 'Debug':
            args.append('-debug')
            args.append('-no-framework')
        else:
            args.append('-release')

        if self.settings.os == 'Android':
            if self.settings.arch == 'x86_64':
                args.append('-android-abis arm64-v8a,armeabi-v7a')
            else:
                args.append('-android-arch')
                args.append('arm64-v8a' if self.settings.arch == 'armv8' else 'armeabi-v7a')
        else:
            args.append('-static')

        if self.settings.os == 'Linux':
            args.append('-no-opengl')

        if self.settings.os == 'iOS':
            args.append('-sdk iphoneos')

            args.append('-qt-host-path')
            args.append(self.qt_host_path)

        if self.settings.os == 'Windows':
            self.run(f"{self.source_folder}/qt5/configure.bat {' '.join(args)}")
        else:
            self.run(f"{self.source_folder}/qt5/configure {' '.join(args)}")

    def build_make(self):
        self.run('cmake --build .')

    def build(self):
        vars = {}

        if is_msvc(self):
            vars = tools.vcvars_dict(self)

            pprint.pprint(vars)

        with tools.environment_append(vars):
            self.build_configure()
            self.build_make()

    def package(self):
        self.run('cmake --install .')
        self.copy('*', src='package', dst='.', excludes='doc/*')

    def package_info(self):
        self.cpp_info.builddirs = [self.package_folder]

    @property
    def xplatform(self):
        if self.settings.os == 'iOS':
            return 'macx-ios-clang'
        if self.settings.os == 'Android':
            return 'android-clang'
        if self.settings.os in ['Windows', 'Linux']:
            return None
        return 'macx-clang'

    @property
    def qt_host_path(self):
        return self.deps_env_info['qt/6.3.0'].rootpath

