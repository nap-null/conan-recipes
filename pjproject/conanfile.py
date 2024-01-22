from conans import ConanFile, AutoToolsBuildEnvironment, tools

class PjProjectConan(ConanFile):
    name = "pjproject"
    version = "2.12.1"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        'shared': [True, False],
    }
    default_options = {
        'shared': True,
    }

    def requirements(self):
        self.requires("OpenSSL/1.1.1q@nap/devel")

    def source(self):
        git = tools.Git()
        git.clone('https://github.com/pjsip/pjproject.git')
        git.checkout(f'{self.version}')

        if self.settings.os == 'Macos':
            tools.replace_in_file(
                'build/rules.mak',
                '$(LD) $(LDOUT)$(subst /,$(HOST_PSEP),$@) ',
                '$(LD) $(LDOUT)$(subst /,$(HOST_PSEP),$@) -install_name @executable_path/../lib/$(@F)'
            )
            tools.replace_in_file(
                'build/rules.mak',
                '-undefined dynamic_lookup -flat_namespace',
                ''
            )

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)

        if self.settings.build_type == 'Debug':
            autotools.flags = ['-O2', '-g']
        else:
            autotools.flags = ['-O2']

        config_options = [
            '--disable-sdl',
            '--disable-ffmpeg',
            f'--with-ssl="{self.openssl_root_dir}"'
        ]

        if self.options.shared:
            config_options.append('--enable-shared')
            config_options.append('--disable-static')
        else:
            config_options.append('--enable-static')
            config_options.append('--disable-shared')

        autotools.configure(args=config_options)
        autotools.make(args=['-j1'])
        autotools.install()

    @property
    def openssl_root_dir(self):
        return self.deps_cpp_info['OpenSSL'].rootpath
