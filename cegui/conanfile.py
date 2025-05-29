#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import get, replace_in_file, collect_libs, patch, copy
import os
import fnmatch


class CeguiConan(ConanFile):
    name = "cegui"
    version = "0.8.x-20200518"
    url = "http://github.com/sixten-hilborn/conan-recipes"
    homepage = "https://github.com/cegui/cegui"
    description = "Crazy Eddie's GUI library is a versatile, fast, adjustable, multi-platform, C++ library for creating graphical user interfaces for games and rendering applications "

    # Indicates License type of the packaged library
    license = "https://opensource.org/licenses/mit-license.php"

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
        "with_sdl": [True, False],
        "build_static_factory_module": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_ogre": False,
        "with_ois": False,
        "with_opengl": False,
        "with_opengl3": False,
        "with_opengles": False,
        "with_sdl": False,
        "build_static_factory_module": True,
    }

    # Use version ranges for dependencies unless there's a reason not to
    requires = (
        "freetype/2.11.1",
        "libxml2/2.9.10",
    )

    short_paths = True

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("build_static_factory_module")

    def requirements(self):
        #self.requires("zlib/1.2.12", override=True)
        if self.options.with_ogre:
            self.requires("ogre/1.11.6@sixten-hilborn/stable")
        if self.options.with_ois:
            self.requires("ois/1.5")
        if self.options.with_sdl:
            self.requires("sdl/2.28.3")
            self.requires("sdl_image/2.0.5")
        else:
            self.requires("freeimage/3.18.0")
        if self.options.with_opengl or self.options.with_opengl3 or self.options.with_opengles:
            self.requires("glew/2.2.0", transitive_headers=True)
            self.requires("glm/0.9.9.8")
            # self.requires("glfw/3.3.2")  # only used for samples, not needed for library


    def source(self):
        commit_id = 'c288602aa95affdab831468ba0a2b34fa1751a6a'
        get(self, f"https://github.com/cegui/cegui/archive/{commit_id}.zip", strip_root=True)

        self._apply_patches('patches', self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        tc.variables['CEGUI_SAMPLES_ENABLED'] = False
        tc.variables['CEGUI_BUILD_PYTHON_MODULES'] = False
        tc.variables['CEGUI_BUILD_APPLICATION_TEMPLATES'] = False
        tc.variables['CEGUI_HAS_FREETYPE'] = True
        tc.variables['CEGUI_OPTION_DEFAULT_IMAGECODEC'] = 'SDL2ImageCodec' if self.options.with_sdl else 'FreeImageImageCodec'
        tc.variables['CEGUI_BUILD_IMAGECODEC_FREEIMAGE'] = not self.options.with_sdl
        tc.variables['CEGUI_BUILD_IMAGECODEC_SDL2'] = self.options.with_sdl
        tc.variables['CEGUI_BUILD_RENDERER_OGRE'] = self.options.with_ogre
        tc.variables['CEGUI_BUILD_RENDERER_OPENGL'] = self.options.with_opengl
        tc.variables['CEGUI_BUILD_RENDERER_OPENGL3'] = self.options.with_opengl3
        tc.variables['CEGUI_BUILD_RENDERER_OPENGLES'] = self.options.with_opengles
        if not self.options.shared:
            tc.variables['CEGUI_BUILD_STATIC_CONFIGURATION'] = True
            tc.variables['CEGUI_BUILD_STATIC_FACTORY_MODULE'] = self.options.build_static_factory_module
        # Help CMake find the libxml2 library file
        libxml2 = self.dependencies["libxml2"]
        if libxml2.cpp_info.libs[0].endswith('_a'):
            fileext = '.lib' if self.settings.os == 'Windows' else '.a'
            tc.variables['LIBXML2_LIBRARIES'] = os.path.join(
                libxml2.package_path,
                libxml2.cpp_info.libdirs[0],
                libxml2.cpp_info.libs[0]+fileext
            ).replace('\\', '/')
        # Help CMake find OGRE
        if self.options.with_ogre:
            tc.variables['OGRE_HOME'] = self.dependencies["ogre"].package_path.as_posix()
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        if not self.options.with_ois:
            replace_in_file(self, f'{self.source_folder}/CMakeLists.txt', 'find_package(OIS)', '')

        replace_in_file(self, f'{self.source_folder}/CMakeLists.txt', 'if(${OGRE_FOUND})', '''if(${OGRE_FOUND})
        if(NOT DEFINED CEGUI_FOUND_OGRE_VERSION_MAJOR)
            string(REPLACE "." ";" OGRE_VERSION_LIST ${OGRE_VERSION})
            list(GET OGRE_VERSION_LIST 0 CEGUI_FOUND_OGRE_VERSION_MAJOR)
            list(GET OGRE_VERSION_LIST 1 CEGUI_FOUND_OGRE_VERSION_MINOR)
            list(GET OGRE_VERSION_LIST 2 CEGUI_FOUND_OGRE_VERSION_PATCH)
        endif()''')

        replace_in_file(self, f'{self.source_folder}/CMakeLists.txt', 'if(NOT ${OGRE_FOUND})', '''if(NOT ${OGRE_FOUND})
            find_package(OGRE)
        endif()
        if(NOT ${OGRE_FOUND})''')

        # Remove VS snprintf workaround
        if self.settings.compiler == 'msvc' and int(str(self.settings.compiler.version)) >= 14:
            replace_in_file(self, f'{self.source_folder}/cegui/include/CEGUI/PropertyHelper.h', '#define snprintf _snprintf', '')

        # Fix issue in FindOgre.cmake when temporary altering CMAKE_FIND_LIBRARY_PREFIXES
        # causing find_library inside CMakeDeps-generated files to fail
        replace_in_file(self, f'{self.source_folder}/cmake/FindOgre.cmake',
            'set(TMP_CMAKE_LIB_PREFIX ${CMAKE_FIND_LIBRARY_PREFIXES})',
            'set(TMP_CMAKE_LIB_PREFIX "${CMAKE_FIND_LIBRARY_PREFIXES}")'
        )
        replace_in_file(self, f'{self.source_folder}/cmake/FindOgre.cmake',
            'set(CMAKE_FIND_LIBRARY_PREFIXES ${TMP_CMAKE_LIB_PREFIX})',
            'set(CMAKE_FIND_LIBRARY_PREFIXES "${TMP_CMAKE_LIB_PREFIX}")'
        )

        # Fix casing for package names
        self._patch_dependency_casing('cegui/src/ImageCodecModules/FreeImage/CMakeLists.txt', new_name='freeimage')
        self._patch_dependency_casing('cegui/src/CMakeLists.txt', new_name='freetype')
        self._patch_dependency_casing('cegui/src/ImageCodecModules/SDL2/CMakeLists.txt', old_name="SDL2IMAGE", new_name='SDL2_image')
        self._patch_dependency_casing('cegui/src/RendererModules/OpenGL/CMakeLists.txt', new_name='glm')
        self._patch_dependency_casing('cegui/src/RendererModules/OpenGL/CMakeLists.txt', new_name='glew')

        # Fix static build issue in Libxml2 module
        replace_in_file(self, f'{self.source_folder}/cegui/include/CEGUI/XMLParserModules/Libxml2/XMLParser.h',
            '#if defined( __WIN32__ ) || defined( _WIN32 )',
            '#if (defined( __WIN32__ ) || defined( _WIN32 )) && !defined(CEGUI_STATIC)')

        cmake = CMake(self)
        cmake.configure()
        cmake.build()


    def package(self):
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can replace all the steps below with the word "pass"
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "include", "CEGUI"), src=os.path.join(self.source_folder, "cegui", "include", "CEGUI"))
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "include", "CEGUI"), src=os.path.join(self.build_folder, "cegui", "include", "CEGUI"))
        if self.options.shared:
            copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, keep_path=False)
            copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            copy(self, pattern="*.so*", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            copy(self, pattern="*.dylib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        else:
            copy(self, pattern="*.a", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            copy(self, pattern="*_Static.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)


    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append('CEGUI_STATIC')
            if self.settings.os == 'Windows':
                self.cpp_info.system_libs.append('Winmm')


    def _apply_patches(self, source, dest):
        for root, _dirnames, filenames in os.walk(source):
            for filename in fnmatch.filter(filenames, '*.patch'):
                patch_file = os.path.join(root, filename)
                dest_path = os.path.join(dest, os.path.relpath(root, source))
                patch(self, base_path=dest_path, patch_file=patch_file)


    def _patch_dependency_casing(self, relative_file, new_name, old_name=None):
        if old_name is None:
            old_name = new_name.upper()
        target = '${CEGUI_TARGET_NAME}'
        replace_in_file(self, f'{self.source_folder}/{relative_file}',
            f'cegui_add_dependency({target} {old_name}',
            f'cegui_add_dependency({target} {new_name}'
        )

