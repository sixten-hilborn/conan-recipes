from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import get, copy
import shutil
import os


class OdeConan(ConanFile):
    name = "ode"
    description = "Open Dynamics Engine is a high performance library for simulating rigid body dynamics"
    version = "0.14"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "double_precision": [True, False],
    }
    default_options = {
        "shared": True,
        "double_precision": False,
    }
    exports_sources = ["CMakeLists.txt", "config.h"]
    url = "http://github.com/sixten-hilborn/conan-recipes"
    homepage = "https://bitbucket.org/odedevs/ode"
    license = "https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html"

    def source(self):
        get(self, f"https://bitbucket.org/odedevs/ode/downloads/ode-{self.version}.tar.gz", strip_root=True)
        #shutil.copy('CMakeLists.txt', self.folder)
        shutil.copy(os.path.join(self.export_sources_folder, 'config.h'), os.path.join(self.source_folder, 'ode', 'src'))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['USE_DOUBLE_PRECISION'] = self.options.double_precision
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include", "ode"), src=os.path.join(self.build_folder, "include", "ode"))
        copy(self, "*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.a", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.so", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, excludes="contrib", keep_path=False)
        copy(self, "*.dylib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)

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
            self.cpp_info.system_libs.append('pthread')
        elif self.settings.os == 'Macos' or self.settings.os == 'iOS':
            self.cpp_info.exelinkflags.append("-framework Carbon")
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags

        self.cpp_info.set_property("cmake_file_name", "ode")
        self.cpp_info.set_property("cmake_target_name", "ODE::ODE")
