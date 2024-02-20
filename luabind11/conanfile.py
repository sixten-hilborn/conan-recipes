from conans import ConanFile, CMake, tools
import os


class Luabind11Conan(ConanFile):
    name = "luabind11"
    version = "0.9.4"
    description = (
        "C++11 fork of luabind, a library to help creating bindings between C++ and Lua"
    )
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": True,
    }
    url = "https://github.com/sixten-hilborn/conan-recipes"
    homepage = "https://github.com/sixten-hilborn/luabind_cpp11"
    license = "MIT - https://opensource.org/licenses/mit-license.php"
    exports = ["CMakeLists.txt", "src*", "luabind*"]
    requires = (
        "lua/5.1.4@sixten-hilborn/stable",
        "boost/1.84.0",
    )

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get(
            url="https://github.com/sixten-hilborn/luabind_cpp11/archive/refs/heads/stable/{}.zip".format(
                self.version
            ),
            destination=self._source_subfolder,
            strip_root=True,
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "include(conanbuildinfo.cmake)",
            "include(../conanbuildinfo.cmake)",
        )

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = os.path.join(
            self.build_folder, "install"
        )
        cmake.definitions["BUILD_TEST"] = False
        cmake.definitions["BUILD_SHARED"] = self.options.shared
        cmake.configure(
            source_folder=self._source_subfolder, build_folder=self._build_subfolder
        )
        cmake.build(target="install")

    def package(self):
        # Headers
        self.copy(pattern="*.h", dst="include", src="install/include", keep_path=True)
        self.copy(pattern="*.hpp", dst="include", src="install/include", keep_path=True)

        # libs
        self.copy(pattern="*.a", dst="lib", src="install/lib", keep_path=False)
        self.copy(pattern="*.so", dst="lib", src="install/lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="install/lib", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="install/lib", keep_path=False)

        # binaries
        self.copy(pattern="*.dll", dst="bin", src="install/bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["luabind11"]
        if self.options.shared:
            self.cpp_info.defines = ["LUABIND_DYNAMIC_LINK"]
