from conans import ConanFile, tools


class OpenSSLConan(ConanFile):
    name = "OpenSSL"
    version = "1.1.1q"
    settings = "os", "arch", "compiler", "build_type"

    patches = []

    options = {
        "shared": [ True, False ],
    }

    default_options = {
        "shared": False,
    }

    def source(self):
        git = tools.Git()
        git.clone('https://github.com/openssl/openssl.git')
        git.checkout('OpenSSL_1_1_1q')
        tools.replace_in_file(
            'Configurations/shared-info.pl',
            '$(INSTALLTOP)/$(LIBDIR)',
            '@executable_path/../lib'
        )

    def build(self):
        options = [
            './Configure',
            'shared' if self.options.shared else 'static',
            'no-tests',
            '--prefix=/',
        ]

        options.append(self.os_and_compiler)

        if self.settings.os == 'Linux' and self.settings.arch == 'armv7':
            options.append('-march=armv7-a')
            options.append('-Wa,--noexecstack')

        if self.settings.build_type == 'Debug':
            options.append('-O2 -g')

        self.run(" ".join(options))
        self.run('make -j')

    def package(self):
        self.run(f'make DESTDIR="{self.package_folder}" install')

        if self.settings.os == 'Linux' and self.settings.arch == 'x86_64':
            with tools.chdir(f'{self.package_folder}'):
                self.run('ln -s lib64 lib')

        with tools.chdir(f'{self.package_folder}'):
            self.run('rm -rf share')

    @property
    def os_and_compiler(self):
        if self.settings.os == 'Linux' and self.settings.arch == 'armv8':
            return 'linux-aarch64'
        if self.settings.os == 'Linux' and self.settings.arch == 'armv7':
            return 'linux-armv4'
        if self.settings.os == 'Linux' and self.settings.arch == 'x86_64':
            return 'linux-x86_64'
        if self.settings.os == 'Macos':
            return 'darwin64-arm64-cc'

        raise 'Unsupported architecture'
