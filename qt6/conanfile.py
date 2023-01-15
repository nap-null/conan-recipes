import os
from conans import ConanFile, CMake, VisualStudioBuildEnvironment, tools
from conan.tools.microsoft import is_msvc
import pprint


class QtConan(ConanFile):
    name = "qt"
    version = "6.4.0"
    settings = "os", "arch", "compiler", "build_type"

    exports = ['patches/*.diff']
    patches = []

    no_copy_source = True
    short_paths = True

    def build_requirements(self):
        if self.settings.os == 'iOS':
            self.build_requires(f"{self.name}/{self.version}")

    def requirements(self):
        if self.settings.os == 'Linux':
            self.requires("OpenSSL/1.1.1q@nap/devel")

    def source(self):
        git = tools.Git(folder='qt')
        git.clone('https://github.com/qt/qt5.git')
        git.checkout('v' + self.version)

        with tools.chdir('qt'):
            self.run('perl init-repository --module-subset=default,-qtwebengine,-qtwebplugin,-qtvirtualkeyboard,-qtgamepad,-qtquick3dphysics')

            for patch in self.patches:
                print(f"Applying patch '{patch}'...")
                self.run(f'git apply ../patches/{patch}')

    def build_configure(self):
        args = [
            '-prefix', os.path.join(self.build_folder, 'package'),
            '-no-feature-designer',
            '-opensource',
            '-confirm-license',
            '-nomake examples',
            '-nomake tests',
        ]

        #if self.settings.os == 'Linux':
        #    args.append('-openssl-linked')

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
            if self.settings.arch != 'armv7':
                args.append('-xcb')

        if self.settings.os == 'iOS':
            args.append('-sdk iphoneos')

            args.append('-qt-host-path')
            args.append(self.qt_host_path)

        if self.settings.os == 'Linux':
            args.append('--')
            args.append('-D')
            args.append(f'OPENSSL_ROOT_DIR="{self.openssl_root_dir}"')

        if self.settings.os == 'Windows':
            self.run(f"{self.source_folder}/qt/configure.bat {' '.join(args)}")
        else:
            self.run(f"{self.source_folder}/qt/configure {' '.join(args)}")

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
        return self.deps_env_info[f'{self.name}/{self.version}'].rootpath

    @property
    def openssl_root_dir(self):
        return self.deps_cpp_info['OpenSSL'].rootpath

