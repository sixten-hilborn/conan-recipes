from conans import CMake, ConanFile, tools
import os

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

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        tools.get("https://github.com/LuaDist/lua/archive/{0}".format(self.zip_name))
        tools.patch(base_path=self.folder, patch_file="CMakeLists.txt.patch")

    def build(self):
        src_dir = os.path.join(self.conanfile_directory, self.folder)
        cmake = CMake(self)
        cmake.definitions['CMAKE_INSTALL_PREFIX'] = os.path.join(self.conanfile_directory, 'install')
        cmake.definitions['BUILD_TESTING'] = False
        cmake.definitions['LUA_BUILD_WLUA'] = False
        cmake.definitions['LUA_BUILD_AS_SHARED'] = self.options.shared
        cmake.configure(build_dir='_build', source_dir=src_dir)
        cmake.build(target='install')

    def package(self):
        self.copy("FindLua.cmake", ".", ".")

        # Headers
        self.copy(pattern="*.h", dst="include", src="install/include", keep_path=True)
        self.copy(pattern="*.hpp", dst="include", src="install/include", keep_path=True)

        # libs
        self.copy(pattern="*.a", dst="lib", src="install/lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src="/install/lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="install/lib", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="install/lib", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src="install/bin", keep_path=False)


    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ['lua']
        else:
            self.cpp_info.libs = ['lua_static']
            if self.settings.compiler == 'gcc':
                self.cpp_info.libs.extend(['m', 'dl'])
