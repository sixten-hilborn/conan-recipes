from conans import ConanFile
from conans.tools import get, patch, replace_in_file
from conans import CMake
from multiprocessing import cpu_count


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
    exports = ["CMakeLists.txt"]
    requires = (
        "openal-soft/1.17.2@R3v3nX/testing"
    )
    url = "http://github.com/sixten-hilborn/conan-alut"
    license = "https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html"

    def source(self):
        #get("https://github.com/vancegroup/freealut/archive/freealut_1_1_0.tar.gz")
        get("https://github.com/vancegroup/freealut/archive/master.zip")

    def requirements(self):
        pass

    def build(self):
        self.makedir('_build')
        cmake = CMake(self.settings)
        cd_build = 'cd _build'
        options = (
            '')
        build_options = '-- -j{0}'.format(cpu_count()) if self.settings.compiler == 'gcc' else ''
        self.run_and_print('%s && cmake .. %s %s' % (cd_build, cmake.command_line, options))
        self.run_and_print("%s && cmake --build . %s %s" % (cd_build, cmake.build_config, build_options))

    def package(self):
        lib_dir = "_build/{0}/lib".format(self.folder)
        bin_dir = "_build/{0}/bin".format(self.folder)
        self.copy(pattern="*.h", dst="include/AL", src="{0}/include".format(self.folder))
        self.copy("*.lib", dst="lib", src=lib_dir, keep_path=False)
        self.copy("*.a", dst="lib", src=lib_dir, keep_path=False)
        self.copy("*.so", dst="lib", src=lib_dir, keep_path=False)
        self.copy("*.dll", dst="bin", src=bin_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = [
            'alut'
        ]

    def makedir(self, path):
        if self.settings.os == "Windows":
            self.run("IF not exist {0} mkdir {0}".format(path))
        else:
            self.run("mkdir {0}".format(path))

    def run_and_print(self, command):
        self.output.warn(command)
        self.run(command)
