from conans import ConanFile
from conans.tools import get, download, SystemPackageTool
import os
import shutil

class CgConan(ConanFile):
    name = "Cg"
    description = "NVIDIA Cg Toolkit"
    version = "3.1"
    generators = "cmake"
    settings = "os", "arch"
    url = "http://github.com/sixten-hilborn/conan-cg"
    license = "https://bitbucket.org/cabalistic/ogredeps/src/bfc878e4fd9a3e026de73114cf42abe2787461b8/src/Cg/license.txt"

    def system_requirements(self):
        if self.settings.os == "Linux":
            installer = SystemPackageTool()
            #installer.install("nvidia-cg-toolkit")
            if self.settings.arch == 'x86':
                installer.install("libc6:i386")
                installer.install("freeglut3:i386")
            elif self.settings.arch == 'x86_64':
                installer.install("libc6:amd64")
                installer.install("freeglut3:amd64")

    def source(self):
        pass

    def build(self):
        if self.settings.os == "Linux":
            self.source_linux()
        elif self.settings.os == "Windows":
            self.source_windows()
        elif self.settings.os == "Macos":
            self.source_mac()

    def source_linux(self):
        if self.settings.arch == 'x86':
            get("http://developer.download.nvidia.com/cg/Cg_3.1/Cg-3.1_April2012_x86.tgz")
        elif self.settings.arch == 'x86_64':
            get("http://developer.download.nvidia.com/cg/Cg_3.1/Cg-3.1_April2012_x86_64.tgz")
        shutil.rmtree("usr/local")

    def source_windows(self):
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

    def source_mac(self):
        download("http://developer.download.nvidia.com/cg/Cg_3.1/Cg-3.1_April2012.dmg", "Cg.dmg")
        self.run("sudo hdiutil attach Cg.dmg")
        self.run('tar -xvf "/Volumes/Cg-3.1.0013/Cg-3.1.0013.app/Contents/Resources/Installer Items/NVIDIA_Cg.tgz" || true')
        self.run("sudo hdiutil detach /Volumes/Cg-3.1.0013")
        lib_path = 'Library/Frameworks/Cg.framework/Versions/1.0'
        self.run('cp -r "{0}" include'.format(lib_path + '/Headers'))
        self.run('cp "{0}" libCg.dylib'.format(lib_path + '/Cg'))
        self.run('chmod -R a+rw .')

    def package(self):
        self.copy(pattern="*.h", dst="include/Cg", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False, links=True)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['Cg']

