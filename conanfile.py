#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil


class Sdl2MixerConan(ConanFile):
    name = "sdl2_mixer"
    version = "2.0.2"
    url = "https://github.com/sixten-hilborn/conan-sdl2_mixer"
    description = "A sample multi-channel audio mixer library."

    # Indicates License type of the packaged library
    license = "zlib License - https://opensource.org/licenses/Zlib"

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
        "with_smpeg": [True, False],
        "with_mpg123": [True, False],
        "with_flac": [True, False],
        "with_ogg": [True, False],
        "with_libmikmod": [True, False],
        "with_libmodplug": [True, False],
        "with_libmad": [True, False]
    }
    default_options = (
        'shared=False',
        'fPIC=True',
        'with_smpeg=False',
        'with_mpg123=True',
        'with_flac=True',
        'with_ogg=True',
        'with_libmikmod=True',
        'with_libmodplug=False',
        'with_libmad=False'
    )

    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    # Use version ranges for dependencies unless there's a reason not to
    requires = "sdl2/[>=2.0.6]@bincrafters/stable"


    def config(self):
        del self.settings.compiler.libcxx


    def requirements(self):
        if self.options.with_smpeg:
            self.requires("smpeg2/[>=2.0.0]@sixten-hilborn/stable")
        if self.options.with_mpg123:
            self.requires("mpg123/1.25.6@sixten-hilborn/stable")
        if self.options.with_flac:
            self.requires("flac/[>=1.3.2]@bincrafters/stable")
        if self.options.with_ogg:
            self.requires("ogg/[>=1.3.3]@bincrafters/stable")
            self.requires("vorbis/[>=1.3.5]@bincrafters/stable")
        if self.options.with_libmikmod:
            self.requires("libmikmod/[>=3.3.11.1]@sixten-hilborn/stable")
        if self.options.with_libmodplug:
            self.requires("libmodplug/[>=0.8.8.5]@sixten-hilborn/stable")
        if self.options.with_libmad:
            self.requires("libmad/[>=0.15.1]@hilborn/stable")


    def source(self):
        extracted_dir = "SDL2_mixer-" + self.version
        tools.get("https://www.libsdl.org/projects/SDL_mixer/release/{0}.tar.gz".format(extracted_dir))

        #Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self.source_subfolder)
        shutil.move("CMakeLists.txt", "{0}/CMakeLists.txt".format(self.source_subfolder))


    def build(self):
        tools.replace_in_file("{0}/music_smpeg.c".format(self.source_subfolder), 'smpeg.SMPEG_actualSpec(mp3, &music_spec);', 'smpeg.SMPEG_actualSpec(music->mp3, &music_spec);')
        tools.replace_in_file("{0}/music_smpeg.c".format(self.source_subfolder), 'stream += (len - left);', 'stream += (len - left); }')
        cmake = CMake(self)
        cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.definitions['SDLMIXER_SUPPORT_OGG_MUSIC'] = self.options.with_ogg
        cmake.definitions['SDLMIXER_SUPPORT_MP3_SMPEG_MUSIC'] = self.options.with_smpeg
        cmake.definitions['SDLMIXER_SUPPORT_MP3_MPG123_MUSIC'] = self.options.with_mpg123
        cmake.definitions['SDLMIXER_SUPPORT_MP3_MAD_MUSIC'] = self.options.with_libmad
        cmake.definitions['SDLMIXER_SUPPORT_FLAC_MUSIC'] = self.options.with_flac
        cmake.definitions['SDLMIXER_SUPPORT_MOD_MODPLUG_MUSIC'] = self.options.with_libmodplug
        cmake.definitions['SDLMIXER_SUPPORT_MOD_MUSIC'] = self.options.with_libmikmod
        cmake.definitions['SDLMIXER_SUPPORT_MID_MUSIC_FLUIDSYNTH'] = False
        cmake.configure(build_folder=self.build_subfolder, source_folder=self.source_subfolder)
        cmake.build()
        cmake.install()


    def package(self):
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can replace all the steps below with the word "pass"
        include_folder = os.path.join(self.source_subfolder, "include")
        self.copy(pattern="LICENSE")
        self.copy(pattern="*SDL_mixer.h", dst="include/SDL2", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", src=self.build_subfolder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=self.build_subfolder, keep_path=False)
        self.copy(pattern="*.a", dst="lib", src=self.build_subfolder, keep_path=False)
        self.copy(pattern="*.so", dst="lib", src=self.build_subfolder, keep_path=False)
        self.copy(pattern="*.so.*", dst="lib", src=self.build_subfolder, keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=self.build_subfolder, keep_path=False)


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs += ["include/SDL2"]
