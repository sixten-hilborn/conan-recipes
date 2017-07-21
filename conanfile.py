from conans import ConanFile, ConfigureEnvironment, CMake
from conans.tools import download, unzip, replace_in_file
import os
import shutil

class SmpegConan(ConanFile):
    name = "smpeg"
    version = "2.0.0"
    description = "smpeg is an mpeg decoding library, which runs on just about any platform"
    folder = "smpeg2-%s" % version
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = (
        'shared=True',
        'fPIC=True'
    )
    generators = "cmake"
    requires = "SDL2/2.0.5@lasote/ci"
    exports = ["CMakeLists.txt"]
    url = "https://github.com/sixten-hilborn/conan-smpeg"
    license = "Library GPL 2.0 - https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html"


    def source(self):
        zip_name = "%s.tar.gz" % self.folder
        download("https://www.libsdl.org/projects/smpeg/release/%s" % zip_name, zip_name)
        unzip(zip_name)
        os.unlink(zip_name)
        shutil.move("CMakeLists.txt", "%s/CMakeLists.txt" % self.folder)
        # Fix "memset" missing
        replace_in_file('%s/audio/MPEGaudio.cpp' % self.folder, '#include "MPEGaudio.h"', '''#include "MPEGaudio.h"
#include <string.h>''')

    def build(self):
        cmake = CMake(self)
        defs = {
            'CMAKE_INSTALL_PREFIX': os.path.join(self.conanfile_directory, 'install'),
            'CMAKE_POSITION_INDEPENDENT_CODE': self.options.fPIC
        }
        src = os.path.join(self.conanfile_directory, self.folder)
        cmake.configure(build_dir='build', source_dir=src, defs=defs)
        cmake.build(target='install')

    def package(self):
        """ Define your conan structure: headers, libs and data. After building your
            project, this method is called to create a defined structure:
        """
        folder = 'install'
        self.copy(pattern="*.h", dst="include", src=folder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=folder, keep_path=False)
        self.copy(pattern="*.dll*", dst="bin", src=folder, keep_path=False)
        self.copy(pattern="*.a", dst="lib", src=folder, keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=folder, keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", src=folder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["smpeg2"]
