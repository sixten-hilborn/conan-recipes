#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from conans.model.version import Version
import os
import fnmatch


class CeguiConan(ConanFile):
    name = "cegui"
    version = "0.8.x-20200518"
    url = "http://github.com/sixten-hilborn/conan-cegui"
    description = "Crazy Eddie's GUI"
    
    # Indicates License type of the packaged library
    license = "https://opensource.org/licenses/mit-license.php"

    # Packages the license for the conanfile.py
    exports = ["LICENSE.md"]
    
    # Remove following lines if the target lib does not use cmake.
    exports_sources = ["CMakeLists.txt", "patches*"]
    generators = "cmake" 
    
    # Options may need to change depending on the packaged library. 
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ogre": [True, False],
        "with_ois": [True, False],
        "with_opengl": [True, False],
        "with_opengl3": [True, False],
        "with_opengles": [True, False],
        "with_sdl": [True, False]
    }
    default_options = (
        "shared=True",
        "fPIC=True",
        "with_ogre=False",
        "with_ois=False",
        "with_opengl=False",
        "with_opengl3=False",
        "with_opengles=False",
        "with_sdl=False",
    )
    
    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    
    # Use version ranges for dependencies unless there's a reason not to
    requires = (
        "freetype/2.10.1",
        "libxml2/2.9.10",
        "libiconv/1.16",  # override to avoid collision between freetype and sdl2
    )

    short_paths = True


    def requirements(self):
        if self.options.with_ogre:
            self.requires("ogre/[>=1.12.0]@sixten-hilborn/stable")
        if self.options.with_ois:
            self.requires("ois/[>=1.3]@sixten-hilborn/stable")
        if self.options.with_sdl:
            self.requires("sdl2/2.0.12@bincrafters/stable")
            self.requires("sdl2_image/2.0.5@bincrafters/stable")
        else:
            self.requires("freeimage/3.18.0@sixten-hilborn/stable")
        if self.options.with_opengl or self.options.with_opengl3 or self.options.with_opengles:
            self.requires("glew/2.1.0@bincrafters/stable")
            self.requires("glm/0.9.9.8")
            self.requires("glfw/3.3.2")


    def source(self):
        commit_id = 'c288602aa95affdab831468ba0a2b34fa1751a6a'
        extracted_dir = self.name + "-" + commit_id
        tools.get("https://github.com/cegui/cegui/archive/{0}.zip".format(commit_id))

        #Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self.source_subfolder)

        self._apply_patches('patches', self.source_subfolder)


    def build(self):
        if not self.options.with_ois:
            tools.replace_in_file('{0}/CMakeLists.txt'.format(self.source_subfolder), 'find_package(OIS)', '')

        # Remove VS snprintf workaround
        if self.settings.compiler == 'Visual Studio' and int(str(self.settings.compiler.version)) >= 14:
            tools.replace_in_file('{0}/cegui/include/CEGUI/PropertyHelper.h'.format(self.source_subfolder), '#define snprintf _snprintf', '')

        cmake = CMake(self)
        cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.definitions['CEGUI_SAMPLES_ENABLED'] = False
        cmake.definitions['CEGUI_BUILD_PYTHON_MODULES'] = False
        cmake.definitions['CEGUI_BUILD_APPLICATION_TEMPLATES'] = False
        cmake.definitions['CEGUI_HAS_FREETYPE'] = True
        cmake.definitions['CEGUI_OPTION_DEFAULT_IMAGECODEC'] = 'SDL2ImageCodec' if self.options.with_sdl else 'FreeImageImageCodec'
        cmake.definitions['CEGUI_BUILD_IMAGECODEC_FREEIMAGE'] = not self.options.with_sdl
        cmake.definitions['CEGUI_BUILD_IMAGECODEC_SDL2'] = self.options.with_sdl
        cmake.definitions['CEGUI_BUILD_RENDERER_OGRE'] = self.options.with_ogre
        cmake.definitions['CEGUI_BUILD_RENDERER_OPENGL'] = self.options.with_opengl
        cmake.definitions['CEGUI_BUILD_RENDERER_OPENGL3'] = self.options.with_opengl3
        cmake.definitions['CEGUI_BUILD_RENDERER_OPENGLES'] = self.options.with_opengles
        # Help CMake find the libxml2 library file
        if self.deps_cpp_info["libxml2"].libs[0].endswith('_a'):
            fileext = '.lib' if self.settings.os == 'Windows' else '.a'
            cmake.definitions['LIBXML2_LIBRARIES'] = os.path.join(self.deps_cpp_info["libxml2"].lib_paths[0], self.deps_cpp_info["libxml2"].libs[0]+fileext)
        # Help CMake find OGRE
        if self.options.with_ogre:
            cmake.definitions['OGRE_HOME'] = self.deps_cpp_info["ogre"].rootpath

        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()


    def package(self):
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can replace all the steps below with the word "pass"
        self.copy(pattern="LICENSE")
        self.copy(pattern="*", dst="include/CEGUI", src="{0}/cegui/include/CEGUI".format(self.source_subfolder))
        self.copy(pattern="*", dst="include/CEGUI", src="{0}/{1}/cegui/include/CEGUI".format(self.build_subfolder, self.source_subfolder))
        self.copy(pattern="*.dll", dst="bin", src=self.build_subfolder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=self.build_subfolder, keep_path=False)
        self.copy(pattern="*.a", dst="lib", src=self.build_subfolder, keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=self.build_subfolder, keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=self.build_subfolder, keep_path=False)

        
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)


    @staticmethod
    def _apply_patches(source, dest):
        for root, _dirnames, filenames in os.walk(source):
            for filename in fnmatch.filter(filenames, '*.patch'):
                patch_file = os.path.join(root, filename)
                dest_path = os.path.join(dest, os.path.relpath(root, source))
                tools.patch(base_path=dest_path, patch_file=patch_file)
