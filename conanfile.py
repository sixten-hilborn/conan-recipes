from conans import ConanFile
import os
from conans.tools import get, patch
from conans import CMake

class LuaConan(ConanFile):
    name = "lua"
    description = "C API of the programming language Lua"
    version = "5.1.4"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False]
    }
    default_options = "shared=True"
    url = "http://github.com/sixten-hilborn/conan-lua"
    license = "https://www.lua.org/license.html"
    exports = "FindLua.cmake", "CMakeLists.txt.patch"
    folder = "lua-{0}".format(version)
    zip_name = "{0}.tar.gz".format(version)

    def source(self):
        get("https://github.com/LuaDist/lua/archive/{0}".format(self.zip_name))
        patch(base_path=self.folder, patch_file="CMakeLists.txt.patch")

    def build(self):
        self.makedir('_build')
        cmake = CMake(self.settings)
        cd_build = 'cd _build'
        options = (
            '-DCMAKE_INSTALL_PREFIX=../_build/install '
            '-DBUILD_TESTING=0 '
            '-DLUA_BUILD_WLUA=0 '
            '-DLUA_BUILD_AS_SHARED={0}'.format(1 if self.options.shared else 0))
        build_options = ''
        self.run_and_print('%s && cmake "../%s" %s %s' % (cd_build, self.folder, cmake.command_line, options))
        self.run_and_print("%s && cmake --build . --target install %s %s" % (cd_build, cmake.build_config, build_options))

    def package(self):
        self.copy("FindLua.cmake", ".", ".")

        # Headers
        self.copy(pattern="*.h", dst="include", src="_build/install/include", keep_path=True)
        self.copy(pattern="*.hpp", dst="include", src="_build/install/include", keep_path=True)

        # libs
        self.copy(pattern="*.a", dst="lib", src="_build/install/lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src="_build/install/lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="_build/install/lib", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="_build/install/lib", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src="_build/install/bin", keep_path=False)


    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ['lua']
        else:
            self.cpp_info.libs = ['lua_static']
            if self.settings.compiler == 'gcc':
                self.cpp_info.libs.extend(['m', 'dl'])

    def makedir(self, path):
        if self.settings.os == "Windows":
            self.run("IF not exist {0} mkdir {0}".format(path))
        else:
            self.run("mkdir {0}".format(path))

    def run_and_print(self, command):
        self.output.info(command)
        self.run(command)
