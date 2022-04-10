#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil


class SmpegConan(ConanFile):
    name = "smpeg"
    version = "2.0.0"
    description = "smpeg is an mpeg decoding library, which runs on just about any platform"
    topics = ("conan", "smpeg", "smpeg2", "mpeg", "sdl")
    url = "https://github.com/sixten-hilborn/conan-smpeg"
    homepage = "https://icculus.org/smpeg"
    author = "Sixten Hilborn <sixten.hilborn@gmail.com>"
    license = "LGPL-2.0"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "sdl/2.0.16"
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        extracted_dir = "smpeg2-" + self.version
        source_url = "https://www.libsdl.org/projects/smpeg/release"
        tools.get("{0}/{1}.tar.gz".format(source_url, extracted_dir))

        # Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self._source_subfolder)

        shutil.move("CMakeLists.txt", "%s/CMakeLists.txt" % self._source_subfolder)
        # Fix "memset" missing
        tools.replace_in_file('%s/audio/MPEGaudio.cpp' % self._source_subfolder, '#include "MPEGaudio.h"', '''#include "MPEGaudio.h"
#include <string.h>''')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
