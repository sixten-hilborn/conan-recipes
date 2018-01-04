#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class LuaConan(ConanFile):
    name = "lua"
    version = "5.1.4"
    url = "http://github.com/sixten-hilborn/conan-lua"
    description = "C API of the programming language Lua"
    
    # Indicates License type of the packaged library
    license = "MIT"
    
    # Packages the license for the conanfile.py
    exports = ["LICENSE.md"]
    
    # Remove following lines if the target lib does not use cmake.
    exports_sources = ["FindLua.cmake", "CMakeLists.txt.patch"]
    generators = "cmake" 
    
    # Options may need to change depending on the packaged library. 
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = (
        "shared=False",
        "fPIC=True"
    )
    
    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
        
    def source(self):
        source_url = "https://github.com/LuaDist/lua"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version

        #Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self.source_subfolder)
        tools.patch(base_path=self.source_subfolder, patch_file="CMakeLists.txt.patch")

        
    def build(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_TESTING'] = False
        cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.definitions['LUA_BUILD_WLUA'] = False
        cmake.definitions['LUA_BUILD_AS_SHARED'] = self.options.shared
        cmake.definitions['SKIP_INSTALL_DATA'] = True
        cmake.configure(build_folder=self.build_subfolder, source_folder=self.source_subfolder)
        cmake.build()
        cmake.install()
        
    def package(self):
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can replace all the steps below with the word "pass"
        include_folder = os.path.join(self.source_subfolder, "include")
        self.copy("FindLua.cmake")
        self.copy(pattern="LICENSE")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler in ['gcc', 'clang']:
            self.cpp_info.libs.extend(['m', 'dl'])
