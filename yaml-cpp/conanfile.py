from conans import ConanFile, CMake, VisualStudioBuildEnvironment, tools


class YAMLCppConan(ConanFile):
    name = "yaml-cpp"
    settings = "os", "arch", "compiler", "build_type"

    no_copy_source = True

    def source(self):
        git = tools.Git()
        git.clone('https://github.com/jbeder/yaml-cpp.git')
        git.checkout(f'{self.name}-{self.version}')

    def build(self):
        cmake = CMake(self)
        cmake.definitions['YAML_CPP_BUILD_TESTS'] = False
        cmake.configure()
        cmake.build()
        cmake.install()
