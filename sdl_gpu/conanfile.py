#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class SdlGpuConan(ConanFile):
    name = "sdl_gpu"
    version = "20171229"
    url = "https://github.com/sixten-hilborn/conan-sdl_gpu"
    description = "A library for high-performance, modern 2D graphics with SDL written in C."
    
    # Indicates License type of the packaged library
    license = "MIT License - https://opensource.org/licenses/MIT"
    
    # Packages the license for the conanfile.py
    exports = ["LICENSE.md"]
    
    # Remove following lines if the target lib does not use cmake.
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake" 
    
    # Options may need to change depending on the packaged library. 
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    
    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    
    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("sdl/2.0.16")

    def system_requirements(self):
        if self.settings.os == "Linux" and tools.os_info.with_apt:
            installer = tools.SystemPackageTool()
            installer.install('mesa-common-dev')
            if 'arm' in str(self.settings.arch):
                installer.install('libgles2-mesa-dev')
            else:
                installer.install('libgl1-mesa-dev')
                installer.install('libglu1-mesa-dev')


    def source(self):
        commit = '143f767adf7d472f81ce890d4692ed29369aa8f3'

        source_url = "https://github.com/grimfang4/sdl-gpu"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, commit))
        extracted_dir = 'sdl-gpu-' + commit

        #Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self.source_subfolder)

        
    def build(self):
        # Patch FindSDL2.cmake to find SDL2
        tools.replace_in_file(
            '{}/scripts/FindSDL2.cmake'.format(self.source_subfolder),
            'find_library(SDL2_LIBRARY NAMES SDL2 sdl2 sdl2 sdl-2.0',
            'find_library(SDL2_LIBRARY NAMES SDL2 sdl2 sdl2 sdl-2.0 SDL2d')

        cmake = CMake(self)
        cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.definitions['SDL_gpu_INSTALL'] = True
        cmake.definitions['SDL_gpu_BUILD_DEMOS'] = False
        cmake.definitions['SDL_gpu_BUILD_SHARED'] = self.options.shared
        cmake.definitions['SDL_gpu_BUILD_STATIC'] = not self.options.shared
        cmake.definitions['SDL_gpu_USE_SDL1'] = self._use_sdl1
        cmake.definitions['SDL_gpu_DISABLE_GLES_1'] = True
        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()
        cmake.install()
        
    def package(self):
        # Libs and headers are already copied via cmake.install()
        self.copy(pattern="LICENSE")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == 'Windows':
            self.cpp_info.libs.append('opengl32')
        elif self.settings.os == 'Linux':
            if 'arm' in str(self.settings.arch):
                self.cpp_info.libs.append('GLESv2')
            else:
                self.cpp_info.libs.append('GL')
        elif self.settings.os == 'Macos':
            self.cpp_info.exelinkflags.append("-framework OpenGL")
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags

        if self._use_sdl1:
            self.cpp_info.includedirs.append("include/SDL")
        else:
            self.cpp_info.includedirs.append("include/SDL2")

    @property
    def _use_sdl1(self):
        vers = self.deps_cpp_info['sdl'].version
        return vers < "2.0.0"
