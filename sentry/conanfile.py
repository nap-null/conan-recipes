from conans import ConanFile, CMake, tools


class SentryConan(ConanFile):
    name = "sentry"
    version = '0.5.3'
    settings = "os", "arch", "compiler", "build_type"

    no_copy_source = True

    def source(self):
        git = tools.Git()
        git.clone('https://github.com/getsentry/sentry-native.git')
        git.checkout(self.version, submodule='recursive')

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()
