from conans import ConanFile, tools
import os
import shutil

class CgConan(ConanFile):
    name = "Cg"
    description = "NVIDIA Cg Toolkit"
    version = "3.1"
    generators = "cmake"
    settings = {"os": ["Linux", "Macos", "Windows"], "arch": ["x86", "x86_64"]}
    url = "http://github.com/sixten-hilborn/conan-cg"
    license = "https://bitbucket.org/cabalistic/ogredeps/src/bfc878e4fd9a3e026de73114cf42abe2787461b8/src/Cg/license.txt"
    exports = ["install_mac.sh"]

    def system_requirements(self):
        if self.settings.os == "Linux":
            installer = tools.SystemPackageTool()
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
            tools.get("http://developer.download.nvidia.com/cg/Cg_3.1/Cg-3.1_April2012_x86.tgz")
        elif self.settings.arch == 'x86_64':
            tools.get("http://developer.download.nvidia.com/cg/Cg_3.1/Cg-3.1_April2012_x86_64.tgz")
        shutil.rmtree("usr/local")

    def source_windows(self):
        def get_cg(path):
            filename = os.path.basename(path)
            tools.download("https://bitbucket.org/cabalistic/ogredeps/raw/bfc878e4fd9a/src/Cg/{0}".format(path), filename)
        get_cg('include/Cg/cg.h')
        if self.settings.arch == 'x86':
            get_cg('bin/cg.dll')
            get_cg('lib/cg.lib')
        else:
            get_cg('bin64/cg.dll')
            get_cg('lib64/cg.lib')

    def source_mac(self):
        tools.download("http://developer.download.nvidia.com/cg/Cg_3.1/Cg-3.1_April2012.dmg", "Cg.dmg")
        self.run("bash -ex ./install_mac.sh")

    def package(self):
        self.copy(pattern="*.h", dst="include/Cg", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False, links=True)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        if self.settings.os == 'Macos':
            self.copy(pattern="*.h", dst="include/Cg", src="/Library/Frameworks/Cg.framework/Versions/1.0/Headers", keep_path=False)

    def package_info(self):
        if self.settings.os == 'Macos':
            self.cpp_info.exelinkflags.append("-iframework /Library/Frameworks")
            self.cpp_info.exelinkflags.append("-framework Cg")
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
        else:
            self.cpp_info.libs = ['Cg']
