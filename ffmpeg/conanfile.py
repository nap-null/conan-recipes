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
        autotools.configure(
            args=[
                '--enable-shared',
                '--disable-asm',
                '--disable-doc',
            ]
        )
        autotools.make()
        autotools.install()
