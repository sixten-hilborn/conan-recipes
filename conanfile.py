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
        options = {
            'BUILD_SHARED_LIBS': self.options.shared,
            'USE_DOUBLE_PRECISION': self.options.double_precision
        }
        cmake.configure(self, build_dir=self.folder, source_dir='.', defs=options)

        build_args = ['--']
        if self.settings.compiler == 'gcc':
            build_args.append('-j{0}'.format(cpu_count()))
        cmake.build(self, args=build_args)

    def package(self):
        bin_dir = "{0}/bin".format(self.folder)
        self.copy(pattern="*.h", dst="include/ode", src="{0}/include/ode".format(self.folder))
        self.copy("*.lib", dst="lib", src=self.folder, keep_path=False)
        self.copy("*.a", dst="lib", src=self.folder, keep_path=False)
        self.copy("*.so", dst="lib", src=self.folder, keep_path=False)
        self.copy("*.dll", dst="bin", src=bin_dir, keep_path=False)
        self.copy("*.dylib", dst="lib", src=self.folder, keep_path=False)

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

        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('pthread')
        elif self.settings.os == 'Macos' or self.settings.os == 'iOS':
            self.cpp_info.exelinkflags.append("-framework Carbon")
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
