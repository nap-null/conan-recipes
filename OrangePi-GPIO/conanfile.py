from conans import ConanFile, tools


class OrangePiGPIOConan(ConanFile):
    name = "OrangePi-GPIO"
    version = "2.0"
    settings = "os", "arch", "compiler", "build_type"

    patches = []

    def source(self):
        git = tools.Git(folder=self.name)
        git.clone('https://github.com/bitia-ru/OrangePi-GPIO.git')
        git.checkout(f'v{self.version}')

    def build(self):
        with tools.chdir(self.name):
            with tools.chdir('wiringPi'):
                self.run('make')

    def package(self):
        with tools.chdir(self.name):
            with tools.chdir('wiringPi'):
                self.run(f'make PREFIX=/ DESTDIR="{self.package_folder}" install')

    def package_info(self):
        self.cpp_info.builddirs = [self.package_folder]
