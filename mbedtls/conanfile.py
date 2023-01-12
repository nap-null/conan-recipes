from conans import ConanFile, CMake, tools


class MbedTLSConan(ConanFile):
    name = "mbedTLS"
    version = '9999'
    settings = "os", "arch", "compiler", "build_type"

    no_copy_source = True

    def source(self):
        git = tools.Git()
        git.clone('https://github.com/Mbed-TLS/mbedtls.git')
        git.checkout('master')

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.components["mbedtls"].names["cmake_find_package"] = "mbedTLS"
        self.cpp_info.components["mbedtls"].libs = [
            f'{self.package_folder}/lib/libmbedtls.a',
            f'{self.package_folder}/lib/libmbedcrypto.a',
        ]
