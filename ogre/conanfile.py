from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import get, replace_in_file, patch, copy, rmdir
from conan.tools.system.package_manager import Apt
from conan.errors import ConanInvalidConfiguration
import os
import fnmatch


def apply_patches(conanfile, source, dest):
    for root, _dirnames, filenames in os.walk(source):
        for filename in fnmatch.filter(filenames, '*.patch'):
            patch_file = os.path.join(root, filename)
            dest_path = os.path.join(dest, os.path.relpath(root, source))
            patch(conanfile, base_path=dest_path, patch_file=patch_file)


class OgreConan(ConanFile):
    name = "ogre"
    version = "1.11.6"
    description = "Open Source 3D Graphics Engine"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "with_rendersystem_d3d9": [True, False],
        "with_rendersystem_d3d11": [True, False],
        "with_rendersystem_gl3plus": [True, False],
        "with_rendersystem_gl": [True, False],
        "with_rendersystem_gles2": [True, False],
        "with_plugin_bsp": [True, False],
        "with_plugin_octree": [True, False],
        "with_plugin_pfx": [True, False],
        "with_plugin_pcz": [True, False],
        "with_plugin_cg": [True, False],
        "with_component_paging": [True, False],
        "with_component_meshlodgenerator": [True, False],
        "with_component_terrain": [True, False],
        "with_component_volume": [True, False],
        "with_component_property": [True, False],
        "with_component_overlay": [True, False],
        "with_component_hlms": [True, False],
        "with_component_bites": [True, False],
        "with_component_python": [True, False],
        "with_component_java": [True, False],
        "with_component_csharp": [True, False],
        "with_component_rtshadersystem": [True, False],
    }
    default_options = {
        "shared": True,
        "freetype/*:shared": False,
        "with_rendersystem_gl3plus": True,
        "with_rendersystem_gl": True,
        "with_rendersystem_gles2": False,
        "with_plugin_bsp": True,
        "with_plugin_octree": True,
        "with_plugin_pfx": True,
        "with_plugin_pcz": True,
        "with_plugin_cg": True,
        "with_component_paging": True,
        "with_component_meshlodgenerator": True,
        "with_component_terrain": True,
        "with_component_volume": True,
        "with_component_property": True,
        "with_component_overlay": True,
        "with_component_hlms": True,
        "with_component_bites": True,
        "with_component_python": False,
        "with_component_java": False,
        "with_component_csharp": False,
        "with_component_rtshadersystem": True,
    }
    exports_sources = ['patches*']
    requires = (
        "freeimage/3.18.0",
        "zlib/1.2.12"
    )
    url = "http://github.com/sixten-hilborn/conan-recipes"
    homepage = "https://github.com/OGRECave/ogre"
    license = "https://opensource.org/licenses/mit-license.php"

    short_paths = True
    
    def config_options(self):
        if self.options.with_rendersystem_d3d9 == None:
            self.options.with_rendersystem_d3d9 = False

        if self.settings.os == 'Windows':
            if self.options.with_rendersystem_d3d11 == None:
                self.options.with_rendersystem_d3d11 = True
        else:
            if self.options.with_rendersystem_d3d11 == None:
                self.options.with_rendersystem_d3d11 = False

    def configure(self):
        if 'x86' not in str(self.settings.arch):  # Ogre's CMake file contains this condition: "Cg_FOUND;NOT APPLE_IOS;NOT WINDOWS_STORE;NOT WINDOWS_PHONE"
            self.options.with_plugin_cg = False

    def requirements(self):
        self.requires("jasper/4.2.0", override=True)  # fixes msvc build error

        if self.options.with_plugin_cg:
            self.requires("cg/3.1@sixten-hilborn/stable")
        if self.options.with_component_overlay:
            self.requires("freetype/2.11.1")
        if self.options.with_component_bites and not self.options.with_component_overlay:
            raise ConanInvalidConfiguration("with_component_bites requires with_component_overlay")
        if not self.options.shared:
            if self.options.with_component_python:
                raise ConanInvalidConfiguration("with_component_python is only supported for shared builds")
            if self.options.with_component_java and self.settings.os != "Android":
                raise ConanInvalidConfiguration("with_component_java is only supported for shared builds")
            if self.options.with_component_csharp:
                raise ConanInvalidConfiguration("with_component_csharp is only supported for shared builds")

    def build_requirements(self):
        if self.settings.os == 'Linux':
            packages = []
            if self._with_opengl():
                packages.extend([
                    'libgl1-mesa-dev',
                    'libglu1-mesa-dev',
                ])
            if self.options.with_rendersystem_gles2:
                packages.append('libgles2-mesa-dev')
            Apt(self).install(packages)

    def system_requirements(self):
        if self.settings.os == 'Linux':
            Apt(self).install([
                'libxmu-dev',
                'libxaw7-dev',
                'libxt-dev',
                'libxrandr-dev',
            ])

    def source(self):
        get(self,
            "https://github.com/OGRECave/ogre/archive/v{0}.zip".format(self.version),
            sha256='43395e72e5c8c1cc7048ae187c57c02eb2a6b52efa1c584f84b000267e6e315b',
            strip_root=True,
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['CMAKE_POSITION_INDEPENDENT_CODE'] = True
        tc.variables['OGRE_STATIC'] = not self.options.shared
        tc.variables['OGRE_COPY_DEPENDENCIES'] = False
        # tc.variables['OGRE_UNITY_BUILD'] = True  # Speed up build
        tc.variables['OGRE_BUILD_DEPENDENCIES'] = False  # Dependencies should be handled via Conan instead :)
        tc.variables['OGRE_BUILD_SAMPLES'] = False
        tc.variables['OGRE_BUILD_TESTS'] = False
        tc.variables['OGRE_BUILD_TOOLS'] = False
        tc.variables['OGRE_INSTALL_PDB'] = False
        tc.variables['OGRE_BUILD_RENDERSYSTEM_D3D9'] = self.options.with_rendersystem_d3d9
        tc.variables['OGRE_BUILD_RENDERSYSTEM_D3D11'] = self.options.with_rendersystem_d3d11
        tc.variables['OGRE_BUILD_RENDERSYSTEM_GL3PLUS'] = self.options.with_rendersystem_gl3plus
        tc.variables['OGRE_BUILD_RENDERSYSTEM_GL'] = self.options.with_rendersystem_gl
        tc.variables['OGRE_BUILD_RENDERSYSTEM_GLES2'] = self.options.with_rendersystem_gles2
        tc.variables['OGRE_BUILD_PLUGIN_BSP'] = self.options.with_plugin_bsp
        tc.variables['OGRE_BUILD_PLUGIN_OCTREE'] = self.options.with_plugin_octree
        tc.variables['OGRE_BUILD_PLUGIN_PFX'] = self.options.with_plugin_pfx
        tc.variables['OGRE_BUILD_PLUGIN_PCZ'] = self.options.with_plugin_pcz
        tc.variables['OGRE_BUILD_PLUGIN_CG'] = self.options.with_plugin_cg
        tc.variables['OGRE_BUILD_COMPONENT_PAGING'] = self.options.with_component_paging
        tc.variables['OGRE_BUILD_COMPONENT_MESHLODGENERATOR'] = self.options.with_component_meshlodgenerator
        tc.variables['OGRE_BUILD_COMPONENT_TERRAIN'] = self.options.with_component_terrain
        tc.variables['OGRE_BUILD_COMPONENT_VOLUME'] = self.options.with_component_volume
        tc.variables['OGRE_BUILD_COMPONENT_PROPERTY'] = self.options.with_component_property
        tc.variables['OGRE_BUILD_COMPONENT_OVERLAY'] = self.options.with_component_overlay
        tc.variables['OGRE_BUILD_COMPONENT_HLMS'] = self.options.with_component_hlms
        tc.variables['OGRE_BUILD_COMPONENT_BITES'] = self.options.with_component_bites
        tc.variables['OGRE_BUILD_COMPONENT_PYTHON'] = self.options.with_component_python
        tc.variables['OGRE_BUILD_COMPONENT_JAVA'] = self.options.with_component_java
        tc.variables['OGRE_BUILD_COMPONENT_CSHARP'] = self.options.with_component_csharp
        tc.variables['OGRE_BUILD_COMPONENT_RTSHADERSYSTEM'] = self.options.with_component_rtshadersystem
        if self.settings.compiler == 'msvc':
            tc.variables['OGRE_CONFIG_STATIC_LINK_CRT'] = str(self.settings.compiler.runtime).startswith('MT')
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_patches(self, 'patches', self.source_folder)
        #replace_in_file(
        #    self,
        #    f'{self.source_folder}/OgreMain/CMakeLists.txt',
        #    '${ZZip_LIBRARIES}',
        #    'ZLIB::ZLIB')
        #replace_in_file(
        #    self,
        #    f'{self.source_folder}/OgreMain/CMakeLists.txt',
        #    'list(APPEND LIBRARIES ZLIB::ZLIB)',
        #    '')
        replace_in_file(
            self,
            f'{self.source_folder}/Components/Overlay/CMakeLists.txt',
            '${FREETYPE_LIBRARIES}',
            'Freetype::Freetype')
        #replace_in_file(
        #    self,
        #    f'{self.source_folder}/Components/Overlay/CMakeLists.txt',
        #    'ZLIB::ZLIB',
        #    'CONAN_PKG::zlib')
        replace_in_file(
            self,
            f'{self.source_folder}/PlugIns/FreeImageCodec/CMakeLists.txt',
            '${FreeImage_LIBRARIES}',
            'freeimage::freeimage')
        replace_in_file(
            self,
            f'{self.source_folder}/Samples/CMakeLists.txt',
            'if (MSVC)',
            'if (MSVC AND OGRE_BUILD_SAMPLES)')

        # Fix for static build without DirectX 9
        if not self.options.with_rendersystem_d3d9:
            replace_in_file(self, f'{self.source_folder}/Components/Bites/CMakeLists.txt', ' ${DirectX9_INCLUDE_DIR}', '')

        #replace_in_file(f'{self.source_folder}/PlugIns/CgProgramManager/include/OgreCgPlugin.h', '#include "OgrePlugin.h"', '#include <OGRE/OgrePlugin.h>')

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "OGRE", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "CMake"))
        rmdir(self, os.path.join(self.package_folder, "media"))


        #sdk_dir = os.path.join(self.build_folder, "_install")
        #cmake = CMake(self)
        #cmake.install(['--prefix', sdk_dir])
        #include_dir = os.path.join(sdk_dir, 'include', 'OGRE')
        #lib_dir = os.path.join(sdk_dir, 'lib')
        #bin_dir = os.path.join(sdk_dir, 'bin')
        #copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include/OGRE"), src=include_dir)
        #copy(self, "*.lib", dst=os.path.join(self.package_folder, "lib"), src=lib_dir, keep_path=False)
        #copy(self, "*.a", dst=os.path.join(self.package_folder, "lib"), src=lib_dir, keep_path=False)
        #copy(self, "*.so*", dst=os.path.join(self.package_folder, "lib"), src=lib_dir, keep_path=False, links=True)
        #copy(self, "*.dylib", dst=os.path.join(self.package_folder, "lib"), src=lib_dir, keep_path=False)
        #copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=bin_dir, keep_path=False)
        ## Copy resource file for Windows dialogs
        #if not self.options.shared and self.settings.os == 'Windows':
        #    copy(self, "*.res", dst=os.path.join(self.package_folder, "res"), src='_build/Components/Bites', keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OGRE")
        self.cpp_info.set_property("cmake_target_name", "OGRE::OGRE")

        # Unfortunately some headers assumes the OGRE directory is an include path
        self.cpp_info.includedirs.append('include/OGRE')

        # All plugins must be linked at compile time instead of dynamically loaded for static builds
        if not self.options.shared:
            if self.options.with_rendersystem_gl:
                self.cpp_info.libs.append('RenderSystem_GL')
            if self.options.with_rendersystem_gl3plus:
                self.cpp_info.libs.append('RenderSystem_GL3Plus')
            if self.options.with_rendersystem_gles2:
                self.cpp_info.libs.append('RenderSystem_GLES2')
            if self.options.with_rendersystem_d3d9:
                self.cpp_info.libs.append('RenderSystem_Direct3D9')
            if self.options.with_rendersystem_d3d11:
                self.cpp_info.libs.append('RenderSystem_Direct3D11')

            if self._with_opengl():
                self.cpp_info.libs.append('OgreGLSupport')

            if self.options.with_plugin_cg:
                self.cpp_info.libs.append('Plugin_CgProgramManager')
            if self.options.with_plugin_bsp:
                self.cpp_info.libs.append('Plugin_BSPSceneManager')
            if self.options.with_plugin_octree:
                self.cpp_info.libs.append('Plugin_OctreeSceneManager')
            if self.options.with_plugin_pfx:
                self.cpp_info.libs.append('Plugin_ParticleFX')
            if self.options.with_plugin_pcz:
                self.cpp_info.libs.append('Plugin_OctreeZone')
                self.cpp_info.libs.append('Plugin_PCZSceneManager')

        self.cpp_info.libs.append('OgreMain')
        if self.options.with_component_overlay:
            self.cpp_info.libs.append('OgreOverlay')
        if self.options.with_component_paging:
            self.cpp_info.libs.append('OgrePaging')
        if self.options.with_component_property:
            self.cpp_info.libs.append('OgreProperty')
        if self.options.with_component_rtshadersystem:
            self.cpp_info.libs.append('OgreRTShaderSystem')
        if self.options.with_component_terrain:
            self.cpp_info.libs.append('OgreTerrain')
        if self.options.with_component_meshlodgenerator:
            self.cpp_info.libs.append('OgreMeshLodGenerator')
        if self.options.with_component_volume:
            self.cpp_info.libs.append('OgreVolume')
        if self.options.with_component_bites:
            self.cpp_info.libs.append('OgreBites')
        if self.options.with_component_hlms:
            self.cpp_info.libs.append('OgreHLMS')


        if not self.options.shared: #and self.settings.os == 'Windows':
            self.cpp_info.libs = [lib+'Static' for lib in self.cpp_info.libs]
        #is_apple = (self.settings.os == 'Macos' or self.settings.os == 'iOS')
        if self.settings.build_type == "Debug" and self.settings.os == 'Windows': #not is_apple:
            self.cpp_info.libs = [lib+'_d' for lib in self.cpp_info.libs]

        if not self.options.shared and self.settings.os == 'Windows':
            # Link against resource file for Windows dialogs
            self.cpp_info.sharedlinkflags.append(os.path.join(self.package_folder, self.cpp_info.resdirs[0], 'OgreWin32Resources.res'))
            self.cpp_info.exelinkflags = self.cpp_info.sharedlinkflags

        if self.settings.os == 'Linux':
            self.cpp_info.system_libs.append('rt')
            if not self.options.shared:
                self.cpp_info.system_libs.append('dl')

    def _with_opengl(self):
        return self.options.with_rendersystem_gl or self.options.with_rendersystem_gl3plus
