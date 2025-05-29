from conan import ConanFile
from conan.tools.files import get, download, copy
from conan.tools.system.package_manager import Apt
from conan.errors import ConanInvalidConfiguration
import os
import shutil


class CgConan(ConanFile):
    name = "cg"
    description = "NVIDIA Cg Toolkit"
    version = "3.1"
    settings = "os", "arch"
    url = "http://github.com/sixten-hilborn/conan-recipes"
    license = "https://bitbucket.org/cabalistic/ogredeps/src/bfc878e4fd9a3e026de73114cf42abe2787461b8/src/Cg/license.txt"
    exports_sources = ["install_mac.sh"]

    options = {
        "shared": [True],
    }
    default_options = {
        "shared": True,
    }

    def validate(self):
        if self.settings.os not in ["Linux", "Macos", "Windows"]:
            raise ConanInvalidConfiguration(f"OS {self.settings.os} not supported")
        if self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration(f"Arch {self.settings.arch} not supported")

    def system_requirements(self):
        if self.settings.os == "Linux":
            ## installer.install("nvidia-cg-toolkit")
            #if (
            #    tools.os_info.linux_distro == "ubuntu"
            #    and tools.os_info.os_version <= "22.04"
            #):
            #    freeglut_lib = "freeglut3"
            #else:
            #    freeglut_lib = "libglut3.12"
            freeglut_lib = "libglut3.12"

            Apt(self).install(["libc6", freeglut_lib])

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
        if self.settings.arch == "x86":
            get(self, "http://developer.download.nvidia.com/cg/Cg_3.1/Cg-3.1_April2012_x86.tgz")
        elif self.settings.arch == "x86_64":
            get(self, "http://developer.download.nvidia.com/cg/Cg_3.1/Cg-3.1_April2012_x86_64.tgz")
        shutil.rmtree("usr/local")

    def source_windows(self):
        def get_cg(path, sha256):
            filename = os.path.basename(path)
            download(
                self,
                f"https://raw.githubusercontent.com/AnotherFoxGuy/cg-toolkit/master/{path}",
                filename,
                sha256=sha256,
            )

        get_cg(
            "include/Cg/cg.h",
            "fdcfeba9b8507437baad347d75c8c2b2599a845b515861bcc535d7af9941c6ed",
        )
        if self.settings.arch == "x86":
            get_cg(
                "bin/cg.dll",
                "d7c5eadbcad39cbb2e6a3ec839d747bf85f3470cf07c9e5c9873546bd6197b2e",
            )
            get_cg(
                "lib/cg.lib",
                "cdaa948eb336fe52194eb15b014bd26683ab05316060766bca0d57f9c22b1fa2",
            )
        else:
            get_cg(
                "bin64/cg.dll",
                "124c758001dd52bd6ef04db670fe93b2107c7d4c9930eed805b766f30418e8fd",
            )
            get_cg(
                "lib64/cg.lib",
                "719e4d54ce5cfdb4173254439ced1427b42793bf697c82a888c67e8bb5ebcbb5",
            )

    def source_mac(self):
        download(
            self,
            "http://developer.download.nvidia.com/cg/Cg_3.1/Cg-3.1_April2012.dmg",
            "Cg.dmg",
        )
        self.run("bash -ex ./install_mac.sh")

    def package(self):
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include", "Cg"), src=self.build_folder, keep_path=False)
        copy(self, "*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.a", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.so*", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.dylib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, keep_path=False)
        if self.settings.os == "Macos":
            copy(
                self,
                pattern="*.h",
                dst=os.path.join(self.package_folder, "include", "Cg"),
                src="/Library/Frameworks/Cg.framework/Versions/1.0/Headers",
                keep_path=False,
            )

    def package_info(self):
        if self.settings.os == "Macos":
            self.cpp_info.exelinkflags.append("-iframework /Library/Frameworks")
            self.cpp_info.exelinkflags.append("-framework Cg")
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
        else:
            self.cpp_info.libs = ["Cg"]
        self.cpp_info.set_property("cmake_file_name", "Cg")
        self.cpp_info.set_property("cmake_target_name", "Cg::Cg")
