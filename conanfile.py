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
        self.makedir('_build')
        cmake = CMake(self.settings)
        cd_build = 'cd _build'
        options = (
            '-DCEGUI_SAMPLES_ENABLED=0 '
            '-DCEGUI_BUILD_PYTHON_MODULES=0 '
            '-DCEGUI_BUILD_APPLICATION_TEMPLATES=0 '
            '-DCEGUI_HAS_FREETYPE=1 '
            '-DCEGUI_OPTION_DEFAULT_IMAGECODEC=FreeImageCodec '
            '-DCEGUI_BUILD_IMAGECODEC_FREEIMAGE=1 ')
        build_options = '-- -j{0}'.format(cpu_count()) if self.settings.compiler == 'gcc' else ''
        self.run_and_print('%s && cmake .. %s %s' % (cd_build, cmake.command_line, options))
        self.run_and_print("%s && cmake --build . %s %s" % (cd_build, cmake.build_config, build_options))

    def makedir(self, path):
        if self.settings.os == "Windows":
            self.run("IF not exist {0} mkdir {0}".format(path))
        else:
            self.run("mkdir {0}".format(path))

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

    def run_and_print(self, command):
        self.output.warn(command)
        self.run(command)
