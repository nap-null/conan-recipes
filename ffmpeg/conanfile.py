from conans import ConanFile, AutoToolsBuildEnvironment, tools


class FFmpegConan(ConanFile):
    name = "ffmpeg"
    version = "4.4"
    settings = "os", "arch", "compiler", "build_type"

    def source(self):
        git = tools.Git()
        git.clone('https://github.com/FFmpeg/FFmpeg.git')
        git.checkout(f'n{self.version}')

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.flags = ['-O2', '-g']

        args = [
            '--enable-shared',
            '--disable-asm',
            '--disable-doc',
        ]

        if self.settings.build_type == 'Debug':
            args.append('--disable-stripping')

        autotools.configure(args=args)
        autotools.make()
        autotools.install()
