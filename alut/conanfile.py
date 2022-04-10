import os
import fnmatch
from conans import ConanFile, CMake, tools


def apply_patches(source, dest):
    for root, dirnames, filenames in os.walk(source):
        for filename in fnmatch.filter(filenames, '*.patch'):
            patch_file = os.path.join(root, filename)
            dest_path = os.path.join(dest, os.path.relpath(root, source))
            tools.patch(base_path=dest_path, patch_file=patch_file)


class AlutConan(ConanFile):
    name = "alut"
    description = "Freealut library for OpenAL"
    version = "1.1.0"
    #folder = 'freealut-freealut_1_1_0'
    folder = 'freealut-master'
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False]
    }
    default_options = "shared=True"
    exports = ["CMakeLists.txt", "patches*"]
    requires = (
        "openal/[>=1.18.2]@bincrafters/stable"
    )
    url = "http://github.com/sixten-hilborn/conan-alut"
    license = "https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html"

    def source(self):
        #tools.get("https://github.com/vancegroup/freealut/archive/freealut_1_1_0.tar.gz")
        tools.get("https://github.com/vancegroup/freealut/archive/master.zip")
        apply_patches('patches', self.folder)

    def requirements(self):
        pass

    def build(self):
        syslibs = ''
        if self.settings.os == 'Windows':
            syslibs = 'Winmm'
        elif self.settings.os == 'Linux':
            syslibs = 'pthread dl'
        alut_cmakelists = "{0}/src/CMakeLists.txt".format(self.folder)
        tools.replace_in_file(alut_cmakelists,
            'target_link_libraries(alut ${OPENAL_LIBRARY})',
            'target_link_libraries(alut ${OPENAL_LIBRARY} %s)' % syslibs)
        # There are some issues with copying files on macos...
        tools.replace_in_file(alut_cmakelists, 'if(NOT WIN32)', 'if(FALSE)')

        cmake = CMake(self)
        cmake.definitions['BUILD_EXAMPLES'] = False
        cmake.definitions['BUILD_STATIC'] = not self.options.shared
        cmake.definitions['BUILD_TESTS'] = False
        cmake.configure(build_dir='_build')
        cmake.build()

    def package(self):
        lib_dir = "_build"
        bin_dir = "_build"
        self.copy(pattern="*.h", dst="include", src="{0}/include".format(self.folder))
        self.copy("*.lib", dst="lib", src=lib_dir, keep_path=False)
        self.copy("*.a", dst="lib", src=lib_dir, keep_path=False)
        if self.options.shared:
            self.copy("*.so*", dst="lib", src=lib_dir, keep_path=False, links=True)
            self.copy("*.dll", dst="bin", src=bin_dir, keep_path=False)
            self.copy("*.dylib", dst="lib", src=bin_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == 'Linux':
            self.cpp_info.libs.extend(['dl', 'pthread', 'm'])
