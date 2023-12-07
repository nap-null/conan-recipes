import os
from conans import ConanFile, tools, __version__
from conans.tools import os_info, SystemPackageTool
from conans.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc


class QtConan(ConanFile):
    name = "qt"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        'shared': [True, False],
    }
    default_options = {
        'shared': True,
    }

    exports = ['patches/*.diff']
    patches = []

    ubuntu_desktop_requires = (
        'libx11-xcb-dev',
        'libxkbcommon-dev',
        'libxkbcommon-x11-dev',
        'libx11-xcb-dev',
        'libxcb*-dev',
    )

    no_copy_source = True
    short_paths = True

    def configure(self):
        if __version__ != '1.60.0':
            raise ConanInvalidConfiguration('This recipe requires conan 1.60.0')

        if self.settings.os == 'Android':
            if not self.options.shared:
                raise ConanInvalidConfiguration('Static builds are not supported on Android')

    def build_requirements(self):
        if self.settings.os in ['iOS', 'Android', 'Emscripten']:
            self.tool_requires(f"{self.name}/{self.version}@nap/devel")

        # TODO: Now I only managed to build Qt with manually install emsdk :(
        # if self.settings.os == 'Emscripten':
        #     self.tool_requires("emsdk/3.1.29")

        if os_info.is_linux:
            if self.settings.arch != 'armv7':
                if os_info.linux_distro != 'ubuntu' or os_info.os_version != '20.04':
                    raise RuntimeError(f'Unsupported Linux: {os_info.linux_distro} {os_info.os_version}')

                installer = SystemPackageTool()
                installer.install_packages(self.ubuntu_desktop_requires)

    def requirements(self):
        if self.settings.os == 'Linux':
            self.requires("OpenSSL/1.1.1q@nap/devel")

    def source(self):
        git = tools.Git(folder='qt')
        git.clone('https://github.com/qt/qt5.git')
        git.checkout('v' + self.version)

        with tools.chdir('qt'):
            disabled_modules = (
                f'-qt{module}'
                for module
                in
                (
                    'webengine',
                    'webplugin',
                    'virtualkeyboard',
                    'gamepad',
                    'quick3dphysics',
                )
            )
            self.run(f"perl init-repository --module-subset=default,{','.join(disabled_modules)}")

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

        if self.xplatform:
            # TODO: Android build fix:
            args.append('-platform')
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
                args.append('-android-abis')
                args.append('arm64-v8a' if self.settings.arch == 'armv8' else 'armeabi-v7a')
            args.append('-android-ndk')
            args.append(os.environ['ANDROID_NDK_ROOT'])
            args.append('-android-sdk')
            args.append(os.environ['ANDROID_SDK_ROOT'])
        else:
            args.append('-shared' if self.options.shared else '-static')

        if self.settings.os == 'Linux':
            args.append('-no-opengl')
            if self.settings.arch != 'armv7':
                args.append('-xcb')

        if self.settings.os == 'iOS':
            args.append('-sdk iphoneos')

        if self.settings.os in ['iOS', 'Android', 'Emscripten']:
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
        if self.settings.os == 'Emscripten':
            return 'wasm-emscripten'
        if self.settings.os in ['Windows', 'Linux']:
            return None
        return 'macx-clang'

    @property
    def qt_host_path(self):
        return self.dependencies.build[self.name].package_folder

    @property
    def openssl_root_dir(self):
        return self.deps_cpp_info['OpenSSL'].rootpath

