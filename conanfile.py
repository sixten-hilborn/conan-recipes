from conans import ConanFile
from conans.tools import get, patch, replace_in_file
from conans import CMake
from multiprocessing import cpu_count
import shutil


class OdeConan(ConanFile):
    name = "ode"
    description = "Open Dynamics Engine is a high performance library for simulating rigid body dynamics"
    version = "0.14"
    folder = 'ode-0.14'
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "double_precision": [True, False]
    }
    default_options = "shared=True", "double_precision=False"
    exports = ["CMakeLists.txt", "config.h"]
    url = "http://github.com/sixten-hilborn/conan-ode"
    license = "https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html"

    def source(self):
        get("https://bitbucket.org/odedevs/ode/downloads/ode-0.14.tar.gz")
        shutil.copy('CMakeLists.txt', self.folder)
        shutil.copy('config.h', self.folder + '/ode/src')

    def build(self):
        cmake = CMake(self.settings)
        cd_build = 'cd ' + self.folder
        options = (
            '-DBUILD_SHARED_LIBS={0} '
            '-DUSE_DOUBLE_PRECISION={1} ').format(
                1 if self.options.shared else 0,
                1 if self.options.double_precision else 0)
        build_options = '-- -j{0}'.format(cpu_count()) if self.settings.compiler == 'gcc' else ''
        self.run_and_print('%s && cmake . %s %s' % (cd_build, cmake.command_line, options))
        self.run_and_print("%s && cmake --build . %s %s" % (cd_build, cmake.build_config, build_options))

    def package(self):
        bin_dir = "{0}/bin".format(self.folder)
        self.copy(pattern="*.h", dst="include/ode", src="{0}/include/ode".format(self.folder))
        self.copy("*.lib", dst="lib", src=self.folder, keep_path=False)
        self.copy("*.a", dst="lib", src=self.folder, keep_path=False)
        self.copy("*.so", dst="lib", src=self.folder, keep_path=False)
        self.copy("*.dll", dst="bin", src=bin_dir, keep_path=False)
        self.copy("*.dylib", dst="bin", src=self.folder, keep_path=False)

    def package_info(self):
        if self.options.double_precision:
            name = 'ode_double'
            self.cpp_info.defines = ['dIDEDOUBLE']
        else:
            name = 'ode_single'
            self.cpp_info.defines = ['dIDESINGLE']

        if self.settings.build_type == 'Debug':
            name += 'd'
        self.cpp_info.libs = [name]

    def run_and_print(self, command):
        self.output.warn(command)
        self.run(command)
