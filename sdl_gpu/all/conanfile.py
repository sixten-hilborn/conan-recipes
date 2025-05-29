#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import get, replace_in_file, collect_libs
from conan.tools.system.package_manager import Apt
import os


class SdlGpuConan(ConanFile):
    name = "sdl_gpu"
    url = "https://github.com/sixten-hilborn/conan-recipes"
    homepage = "https://github.com/grimfang4/sdl-gpu"
    description = (
        "A library for high-performance, modern 2D graphics with SDL written in C."
    )

    license = "MIT License - https://opensource.org/licenses/MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        self.requires("sdl/2.0.16", transitive_headers=True)

    def system_requirements(self):
        packages = ["mesa-common-dev"]
        if "arm" in str(self.settings.arch):
            packages.append("libgles2-mesa-dev")
        else:
            packages.extend([
                "libgl1-mesa-dev",
                "libglu1-mesa-dev",
            ])
        Apt(self).install(packages)

    def source(self):
        get(self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SDL_gpu_INSTALL"] = True
        tc.variables["SDL_gpu_BUILD_DEMOS"] = False
        tc.variables["SDL_gpu_BUILD_SHARED"] = self.options.shared
        tc.variables["SDL_gpu_BUILD_STATIC"] = not self.options.shared
        tc.variables["SDL_gpu_USE_SDL1"] = self._use_sdl1
        tc.variables["SDL_gpu_DISABLE_GLES_1"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        # Patch FindSDL2.cmake to find SDL2
        replace_in_file(
            self,
            f"{self.source_folder}/scripts/FindSDL2.cmake",
            "find_library(SDL2_LIBRARY NAMES SDL2 sdl2 sdl2 sdl-2.0",
            "find_library(SDL2_LIBRARY NAMES SDL2 sdl2 sdl2 sdl-2.0 SDL2d",
        )
        replace_in_file(
            self,
            f"{self.source_folder}/CMakeLists.txt",
            "find_package(Doxygen)",
            "set(DOXYGEN_FOUND FALSE) #find_package(Doxygen)",
        )

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SDL_gpu")
        self.cpp_info.set_property("cmake_target_name", "SDL_gpu::SDL_gpu")

        self.cpp_info.libs = collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("opengl32")
        elif self.settings.os == "Linux":
            if "arm" in str(self.settings.arch):
                self.cpp_info.system_libs.append("GLESv2")
            else:
                self.cpp_info.system_libs.append("GL")
        elif self.settings.os == "Macos":
            self.cpp_info.exelinkflags.append("-framework OpenGL")
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags

        if self._use_sdl1:
            self.cpp_info.includedirs.append("include/SDL")
        else:
            self.cpp_info.includedirs.append("include/SDL2")

    @property
    def _use_sdl1(self):
        vers = self.dependencies["sdl"].ref.version
        return vers < "2.0.0"
