import os
import shutil
from conans import ConanFile, CMake
from conans.tools import get


class SdlGpuConan(ConanFile):
    name = "SDL_gpu"
    version = "0.11.0"
    description = "A library for high-performance, modern 2D graphics with SDL written in C."
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_sdl1": [True, False],
    }
    default_options = (
        'fPIC=True',
        'use_sdl1=False'
    )
    generators = "cmake"
    exports = ["CMakeLists.txt"]
    url = "https://github.com/sixten-hilborn/conan-sdl_gpu"
    license = "MIT License - https://opensource.org/licenses/MIT"

    def config(self):
        del self.settings.compiler.libcxx

    def configure(self):
        sdl = 'SDL' if self.options.use_sdl1 else 'SDL2'
        sdl_shared = self.options[sdl].shared
        if sdl_shared is None:
            sdl_shared = False

        if self.options.shared.value is None:
            self.options.shared = sdl_shared

        if self.options.shared != sdl_shared:
            message = 'SDL_gpu:shared ({0}) must be the same as {1}:shared ({2})'.format(
                self.options.shared, sdl, sdl_shared)
            raise Exception(message)

    def requirements(self):
        if self.options.use_sdl1:
            # Does not exist at the moment, but can be overridden
            self.requires("SDL/1.2.15@conan/stable")
        else:
            self.requires("SDL2/2.0.5@lasote/ci")

    def source(self):
        commit = '6f6fb69b56363182d693b3fb8eb2b2b1853a9565'
        get('https://github.com/grimfang4/sdl-gpu/archive/{0}.tar.gz'.format(commit))
        shutil.move('sdl-gpu-{0}'.format(commit), 'sdl-gpu')

    def build(self):
        cmake = CMake(self)
        defs = {
            'CMAKE_INSTALL_PREFIX': os.path.join(self.conanfile_directory, 'install'),
            'CMAKE_POSITION_INDEPENDENT_CODE': self.options.fPIC,
            'SDL_gpu_INSTALL': True,
            'SDL_gpu_BUILD_DEMOS': False,
            'SDL_gpu_BUILD_SHARED': self.options.shared,
            'SDL_gpu_BUILD_STATIC': not self.options.shared,
            'SDL_gpu_USE_SDL1': self.options.use_sdl1
        }
        cmake.configure(build_dir='build', defs=defs)
        cmake.build(target='install')

    def package(self):
        """ Define your conan structure: headers, libs and data. After building your
            project, this method is called to create a defined structure:
        """
        folder = 'install'
        self.copy(pattern="*SDL_gpu*.h", dst=self._include_dir(), src=folder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=folder, keep_path=False)
        self.copy(pattern="*.dll*", dst="bin", src=folder, keep_path=False)
        self.copy(pattern="*.a", dst="lib", src=folder, keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=folder, keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", src=folder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["SDL_gpu"] if self.options.use_sdl1 else ["SDL2_gpu"]
        self.cpp_info.includedirs += [self._include_dir()]

    def _include_dir(self):
        if self.options.use_sdl1:
            return "include/SDL"
        else:
            return "include/SDL2"
