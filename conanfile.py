import os
import fnmatch
from conans import CMake, ConanFile
from conans.tools import get, patch, replace_in_file


def apply_patches(source, dest):
    for root, _dirnames, filenames in os.walk(source):
        for filename in fnmatch.filter(filenames, '*.patch'):
            patch_file = os.path.join(root, filename)
            dest_path = os.path.join(dest, os.path.relpath(root, source))
            patch(base_path=dest_path, patch_file=patch_file)


class CeguiConan(ConanFile):
    name = "CEGUI"
    description = "Crazy Eddie's GUI"
    version = "0.8.7"
    folder = 'cegui-0.8.7'
    generators = "cmake"
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
        "with_ogre=True",
        "with_ois=True",
        "with_opengl=False",
        "with_opengl3=False",
        "with_opengles=False",
        "with_sdl=False",
        "libxml2:shared=True"
    )
    exports = ["CMakeLists.txt", 'patches*']
    requires = (
        "freetype/2.6.3@hilborn/stable",
        "libxml2/2.9.3@hilborn/stable"
    )
    url = "http://github.com/sixten-hilborn/conan-cegui"
    license = "https://opensource.org/licenses/mit-license.php"

    short_paths = True

    def source(self):
        get("https://bitbucket.org/cegui/cegui/downloads/cegui-0.8.7.zip")
        apply_patches('patches', self.folder)
        if not self.options.with_ois:
            replace_in_file('{0}/CMakeLists.txt'.format(self.folder), 'find_package(OIS)', '')

    def requirements(self):
        if self.options.with_ogre:
            self.requires("OGRE/1.9.0@hilborn/stable")
        if self.options.with_ois:
            self.requires("OIS/1.3@hilborn/stable")
        if self.options.with_sdl:
            self.requires("SDL2/2.0.5@lasote/ci")
            self.requires("SDL2_image/2.0.1@lasote/stable")
        else:
            self.requires("freeimage/3.17.0@hilborn/stable")
        if self.options.with_opengl or self.options.with_opengl3 or self.options.with_opengles:
            #self.requires("glew/2.0.0@coding3d/stable")
            self.requires("glew/1.13.0@coding3d/stable")
            self.requires("glm/0.9.8.4@coding3d/stable")
            self.requires("glfw/3.2.1@coding3d/stable")

    def build(self):
        cmake = CMake(self)
        options = {
            'CEGUI_SAMPLES_ENABLED': False,
            'CEGUI_BUILD_PYTHON_MODULES': False,
            'CEGUI_BUILD_APPLICATION_TEMPLATES': False,
            'CEGUI_HAS_FREETYPE': True,
            'CEGUI_OPTION_DEFAULT_IMAGECODEC': 'SDL2ImageCodec' if self.options.with_sdl else 'FreeImageCodec',
            'CEGUI_BUILD_IMAGECODEC_FREEIMAGE': not self.options.with_sdl,
            'CEGUI_BUILD_IMAGECODEC_SDL2': self.options.with_sdl,
            'CEGUI_BUILD_RENDERER_OGRE': self.options.with_ogre,
            'CEGUI_BUILD_RENDERER_OPENGL': self.options.with_opengl,
            'CEGUI_BUILD_RENDERER_OPENGL3': self.options.with_opengl3,
            'CEGUI_BUILD_RENDERER_OPENGLES': self.options.with_opengles,
        }
        cmake.configure(build_dir='_build', defs=options)
        cmake.build()

    def package(self):
        lib_dir = "_build/{0}/lib".format(self.folder)
        bin_dir = "_build/{0}/bin".format(self.folder)
        self.copy(pattern="*.h", dst="include/CEGUI", src="{0}/cegui/include/CEGUI".format(self.folder))
        self.copy(pattern="*.h", dst="include/CEGUI", src="_build/{0}/cegui/include/CEGUI".format(self.folder))
        self.copy("*.lib", dst="lib", src=lib_dir, keep_path=False)
        self.copy("*.a", dst="lib", src=lib_dir, keep_path=False)
        self.copy("*.so*", dst="lib", src=lib_dir, keep_path=False, links=True)
        self.copy("*.dll", dst="bin", src=bin_dir, keep_path=False)
        self.copy("*.dylib", dst="lib", src=bin_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['CEGUIBase-0']

        if self.options.with_ogre:
            self.cpp_info.libs.append('CEGUIOgreRenderer-0')
        if self.options.with_opengl or self.options.with_opengl3:
            self.cpp_info.libs.append('CEGUIOpenGLRenderer-0')

        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio":
                self.cpp_info.libs = [lib+'_d' for lib in self.cpp_info.libs]

