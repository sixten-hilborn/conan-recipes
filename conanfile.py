import os
import fnmatch
from shutil import copytree
from conans import ConanFile
from conans.tools import get, patch, replace_in_file
from conans import CMake
from multiprocessing import cpu_count


def apply_patches(source, dest):
    for root, dirnames, filenames in os.walk(source):
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
        "with_ois": [True, False]
    }
    default_options = "shared=True", "with_ois=False", "libxml2:shared=True"
    exports = ["CMakeLists.txt", 'patches*']
    requires = (
        "freeimage/3.17.0@hilborn/stable",
        "freetype/2.6.3@hilborn/stable",
        "OGRE/1.9.0@hilborn/stable",
        "OIS/1.3@hilborn/stable",
        "libxml2/2.9.3@lasote/stable"
        #"SDL2/2.0.5@lasote/stable",
        #"SDL2_image/2.0.1@lasote/stable"
    )
    url = "http://github.com/sixten-hilborn/conan-cegui"
    license = "https://opensource.org/licenses/mit-license.php"

    def source(self):
        get("https://bitbucket.org/cegui/cegui/downloads/cegui-0.8.7.zip")
        apply_patches('patches', self.folder)
        if not self.options.with_ois:
            replace_in_file('{0}/CMakeLists.txt'.format(self.folder), 'find_package(OIS)', '')

    def requirements(self):
        if self.options.with_ois:
            self.requires("OIS/1.3@hilborn/stable")

    def build(self):
        cmake = CMake(self.settings)
        options = {
            'CEGUI_SAMPLES_ENABLED': False,
            'CEGUI_BUILD_PYTHON_MODULES': False,
            'CEGUI_BUILD_APPLICATION_TEMPLATES': False,
            'CEGUI_HAS_FREETYPE': True,
            'CEGUI_OPTION_DEFAULT_IMAGECODEC': 'FreeImageCodec',
            'CEGUI_BUILD_IMAGECODEC_FREEIMAGE': True
        }
        cmake.configure(self, build_dir='_build', defs=options)
        build_args = ['--']
        if self.settings.compiler == 'gcc':
            build_args.append('-j{0}'.format(cpu_count()))
        cmake.build(self, args=build_args)

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
        self.cpp_info.libs = [
            'CEGUIBase-0',
            'CEGUIOgreRenderer-0'
        ]

        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio":
                self.cpp_info.libs = [lib+'_d' for lib in self.cpp_info.libs]

