import glob
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class PjProjectConan(ConanFile):
    name = "pjproject"
    version = "2.12.1"
    settings = "os", "arch", "compiler", "build_type"

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
        autotools.flags = ['-O2', '-g']
        autotools.configure(
            args=[
                '--enable-shared',
                '--disable-sdl',
                '--disable-ffmpeg',
                f'--with-ssl="{self.openssl_root_dir}"'
            ]
        )
        autotools.make(args=['-j1'])
        autotools.install()

    #def package(self):
    #    with tools.chdir(self.package_folder + "/lib"):
    #        for file in list(glob.glob('*.dylib')):
    #            self.run(f"install_name_tool -id @executable_path/../lib/{file} {file}")

    @property
    def openssl_root_dir(self):
        return self.deps_cpp_info['OpenSSL'].rootpath
