#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil


class SmpegConan(ConanFile):
    name = "smpeg2"
    version = "2.0.0"
    url = "https://github.com/sixten-hilborn/conan-smpeg"
    description = "smpeg is an mpeg decoding library, which runs on just about any platform"

    # Indicates License type of the packaged library
    license = "Library GPL 2.0 - https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html"

    # Packages the license for the conanfile.py
    exports = ["LICENSE.md"]

    # Remove following lines if the target lib does not use cmake.
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake" 

    # Options may need to change depending on the packaged library. 
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = (
        'fPIC=True'
    )

    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    
    # Use version ranges for dependencies unless there's a reason not to
    requires = (
        "sdl2/[>=2.0.5]@bincrafters/stable"
    )

    def configure(self):
        sdl_shared = self.options['sdl2'].shared
        if sdl_shared is None:
            sdl_shared = False

        if self.options.shared.value is None:
            self.options.shared = sdl_shared

        if self.options.shared != sdl_shared:
            message = 'smpeg:shared ({0}) must be the same as sdl2:shared ({1})'.format(
                self.options.shared, sdl_shared)
            raise Exception(message)


    def source(self):
        extracted_dir = self.name + "-" + self.version
        source_url = "https://www.libsdl.org/projects/smpeg/release"
        tools.get("{0}/{1}.tar.gz".format(source_url, extracted_dir))

        #Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self.source_subfolder)

        shutil.move("CMakeLists.txt", "%s/CMakeLists.txt" % self.source_subfolder)
        # Fix "memset" missing
        tools.replace_in_file('%s/audio/MPEGaudio.cpp' % self.source_subfolder, '#include "MPEGaudio.h"', '''#include "MPEGaudio.h"
#include <string.h>''')

        
    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.configure(build_folder=self.build_subfolder, source_folder=self.source_subfolder)
        cmake.build()
        cmake.install()

        
    def package(self):
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can replace all the steps below with the word "pass"
        include_folder = os.path.join(self.source_subfolder, "include")
        self.copy(pattern="LICENSE")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

        
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
