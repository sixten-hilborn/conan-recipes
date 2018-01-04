#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import fnmatch


class CeguiConan(ConanFile):
    name = "cegui"
    version = "0.8.7"
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
        "with_ogre": [True, False],
        "with_ois": [True, False],
        "with_opengl": [True, False],
        "with_opengl3": [True, False],
        "with_opengles": [True, False],
        "with_sdl": [True, False]
    }
    default_options = (
        "shared=True",
        "with_ogre=False",
        "with_ois=False",
        "with_opengl=False",
        "with_opengl3=False",
        "with_opengles=False",
        "with_sdl=False",
        "libxml2:shared=True"
    )
    
    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    
    # Use version ranges for dependencies unless there's a reason not to
    requires = (
        "freetype/[>=2.8.1]@bincrafters/stable",
        "libxml2/[>=2.9.3]@bincrafters/stable"
    )

    short_paths = True


    def requirements(self):
        if self.options.with_ogre:
            self.requires("OGRE/[>=1.9.0]@sixten-hilborn/stable")
        if self.options.with_ois:
            self.requires("OIS/[>=1.3]@sixten-hilborn/stable")
        if self.options.with_sdl:
            self.requires("sdl2/[>=2.0.5]@bincrafters/stable")
            self.requires("sdl2_image/[>=2.0.1]@sixten-hilborn/stable")
        else:
            self.requires("freeimage/[>=3.17.0]@sixten-hilborn/stable")
        if self.options.with_opengl or self.options.with_opengl3 or self.options.with_opengles:
            #self.requires("glew/2.0.0@coding3d/stable")
            self.requires("glew/1.13.0@coding3d/stable")
            self.requires("glm/[>=0.9.8.5]@g-truc/stable")
            self.requires("glfw/[>=3.2.1]@bincrafters/stable")


    def source(self):
        extracted_dir = self.name + "-" + self.version
        source_url = "https://bitbucket.org/cegui/cegui"
        tools.get("{0}/downloads/{1}.zip".format(source_url, extracted_dir))

        #Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self.source_subfolder)

        _apply_patches('patches', self.source_subfolder)


    def build(self):
        if not self.options.with_ois:
            tools.replace_in_file('{0}/CMakeLists.txt'.format(self.source_subfolder), 'find_package(OIS)', '')

        cmake = CMake(self)
        cmake.definitions['CEGUI_SAMPLES_ENABLED'] = False
        cmake.definitions['CEGUI_BUILD_PYTHON_MODULES'] = False
        cmake.definitions['CEGUI_BUILD_APPLICATION_TEMPLATES'] = False
        cmake.definitions['CEGUI_HAS_FREETYPE'] = True
        cmake.definitions['CEGUI_OPTION_DEFAULT_IMAGECODEC'] = 'SDL2ImageCodec' if self.options.with_sdl else 'FreeImageCodec'
        cmake.definitions['CEGUI_BUILD_IMAGECODEC_FREEIMAGE'] = not self.options.with_sdl
        cmake.definitions['CEGUI_BUILD_IMAGECODEC_SDL2'] = self.options.with_sdl
        cmake.definitions['CEGUI_BUILD_RENDERER_OGRE'] = self.options.with_ogre
        cmake.definitions['CEGUI_BUILD_RENDERER_OPENGL'] = self.options.with_opengl
        cmake.definitions['CEGUI_BUILD_RENDERER_OPENGL3'] = self.options.with_opengl3
        cmake.definitions['CEGUI_BUILD_RENDERER_OPENGLES'] = self.options.with_opengles
        cmake.configure(build_folder=self.build_subfolder)
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

        #lib_dir = "_build/{0}/lib".format(self.folder)
        #bin_dir = "_build/{0}/bin".format(self.folder)
        #self.copy(pattern="*.h", dst="include/CEGUI", src="{0}/cegui/include/CEGUI".format(self.folder))
        #self.copy(pattern="*.h", dst="include/CEGUI", src="_build/{0}/cegui/include/CEGUI".format(self.folder))
        #self.copy("*.lib", dst="lib", src=lib_dir, keep_path=False)
        #self.copy("*.a", dst="lib", src=lib_dir, keep_path=False)
        #self.copy("*.so*", dst="lib", src=lib_dir, keep_path=False, links=True)
        #self.copy("*.dll", dst="bin", src=bin_dir, keep_path=False)
        #self.copy("*.dylib", dst="lib", src=bin_dir, keep_path=False)

        
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)


    @staticmethod
    def _apply_patches(source, dest):
        for root, _dirnames, filenames in os.walk(source):
            for filename in fnmatch.filter(filenames, '*.patch'):
                patch_file = os.path.join(root, filename)
                dest_path = os.path.join(dest, os.path.relpath(root, source))
                tools.patch(base_path=dest_path, patch_file=patch_file)
