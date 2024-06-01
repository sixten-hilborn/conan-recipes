from conans import ConanFile, tools
import os
import shutil


class CgConan(ConanFile):
    name = "cg"
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
            # installer.install("nvidia-cg-toolkit")
            if (
                tools.os_info.linux_distro == "ubuntu"
                and tools.os_info.os_version <= "22.04"
            ):
                freeglut_lib = "freeglut3"
            else:
                freeglut_lib = "libglut3.12"

            arch_suffix = "i386" if self.settings.arch == "x86" else "amd64"

            installer.install(f"libc6:{arch_suffix}")
            installer.install(f"{freeglut_lib}:{arch_suffix}")

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
            tools.get(
                "http://developer.download.nvidia.com/cg/Cg_3.1/Cg-3.1_April2012_x86.tgz"
            )
        elif self.settings.arch == "x86_64":
            tools.get(
                "http://developer.download.nvidia.com/cg/Cg_3.1/Cg-3.1_April2012_x86_64.tgz"
            )
        shutil.rmtree("usr/local")

    def source_windows(self):
        def get_cg(path, sha256):
            filename = os.path.basename(path)
            tools.download(
                "https://raw.githubusercontent.com/AnotherFoxGuy/cg-toolkit/master/{0}".format(
                    path
                ),
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
        tools.download(
            "http://developer.download.nvidia.com/cg/Cg_3.1/Cg-3.1_April2012.dmg",
            "Cg.dmg",
        )
        self.run("bash -ex ./install_mac.sh")

    def package(self):
        self.copy(pattern="*.h", dst="include/Cg", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False, links=True)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        if self.settings.os == "Macos":
            self.copy(
                pattern="*.h",
                dst="include/Cg",
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
