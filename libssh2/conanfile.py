from conans import ConanFile, CMake, tools


class LibSSH2Conan(ConanFile):
    name = "ssh2"
    version = '9999'
    settings = "os", "arch", "compiler", "build_type"

    no_copy_source = True

    def requirements(self):
        self.requires("OpenSSL/1.1.1q@nap/devel")

    def source(self):
        git = tools.Git()
        git.clone('https://github.com/libssh2/libssh2.git')
        git.checkout('master')

    def build(self):
        cmake = CMake(self)
        cmake.definitions['CRYPTO_BACKEND'] = 'OpenSSL'
        cmake.definitions['OPENSSL_ROOT_DIR'] = self.openssl_root_dir
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        with tools.chdir(f'{self.package_folder}'):
            self.run('rm -rf lib/cmake share')

    @property
    def openssl_root_dir(self):
        return self.deps_cpp_info['OpenSSL'].rootpath
