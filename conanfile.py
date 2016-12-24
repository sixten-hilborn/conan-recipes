from conans import ConanFile
from conans.tools import download
from conans import CMake
import os

class CgConan(ConanFile):
    name = "Cg"
    description = "NVIDIA Cg Toolkit"
    version = "3.1"
    generators = "cmake"
    settings = "os", "arch"
    url = "http://github.com/sixten-hilborn/conan-cg"
    license = "https://bitbucket.org/cabalistic/ogredeps/src/bfc878e4fd9a3e026de73114cf42abe2787461b8/src/Cg/license.txt"

    def source(self):
        if self.settings.os == "Linux":
            self.output.warn("Using apt-get to install Cg")
            self.run("sudo apt-get update && sudo apt-get install -y nvidia-cg-toolkit")
        elif self.settings.os == "Windows":
            def get_cg(path):
                filename = os.path.basename(path)
                download("https://bitbucket.org/cabalistic/ogredeps/raw/bfc878e4fd9a/src/Cg/{0}".format(path), filename)
            get_cg('include/Cg/cg.h')
            if self.settings.arch == 'x86':
                get_cg('bin/cg.dll')
                get_cg('lib/cg.lib')
            else:
                get_cg('bin64/cg.dll')
                get_cg('lib64/cg.lib')

    def build(self):
        pass

    def package(self):
        self.copy(pattern="*.h", dst="include/Cg", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['Cg']

