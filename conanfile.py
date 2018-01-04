from conans import ConanFile, CMake
from conans.tools import download, unzip, replace_in_file
import os
import shutil

class Sdl2MixerConan(ConanFile):
    name = "SDL2_mixer"
    version = "2.0.1"
    description = "SDL2_mixer is a sample multi-channel audio mixer library."
    folder = "SDL2_mixer-%s" % version
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_smpeg": [True, False],
        "with_flac": [True, False],
        "with_ogg": [True, False],
        "with_libmikmod": [True, False],
        "with_libmodplug": [True, False],
        "with_libmad": [True, False]
    }
    default_options = (
        'shared=False',
        'fPIC=True',
        'with_smpeg=True',
        'with_flac=True',
        'with_ogg=True',
        'with_libmikmod=True',
        'with_libmodplug=False',
        'with_libmad=False'
    )
    generators = "cmake"
    requires = "sdl2/[>=2.0.6]@bincrafters/stable"
    exports = ["CMakeLists.txt"]
    url = "https://github.com/sixten-hilborn/conan-sdl2_mixer"
    license = "zlib License - https://opensource.org/licenses/Zlib"

    def config(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_smpeg:
            self.requires("smpeg/2.0.0@hilborn/stable")
        if self.options.with_flac:
            self.requires("flac/[>=1.3.2]@bincrafters/stable")
        if self.options.with_ogg:
            self.requires("ogg/[>=1.3.3]@bincrafters/stable")
            self.requires("vorbis/[>=1.3.5]@bincrafters/stable")
        if self.options.with_libmikmod:
            self.requires("libmikmod/3.3.11.1@hilborn/stable")
        if self.options.with_libmodplug:
            self.requires("libmodplug/0.8.8.5@hilborn/stable")
        if self.options.with_libmad:
            self.requires("libmad/0.15.1@hilborn/stable")

    def source(self):
        zip_name = "%s.tar.gz" % self.folder
        download("https://www.libsdl.org/projects/SDL_mixer/release/%s" % zip_name, zip_name)
        unzip(zip_name)
        os.unlink(zip_name)
        shutil.move("CMakeLists.txt", "%s/CMakeLists.txt" % self.folder)

    def build(self):
        cmake = CMake(self)
        defs = {
            'CMAKE_INSTALL_PREFIX': os.path.join(self.conanfile_directory, 'install'),
            'CMAKE_POSITION_INDEPENDENT_CODE': self.options.fPIC,
            'SDLMIXER_SUPPORT_OGG_MUSIC': self.options.with_ogg,
            'SDLMIXER_SUPPORT_MP3_MUSIC': self.options.with_smpeg,
            'SDLMIXER_SUPPORT_MP3_MAD_MUSIC': self.options.with_libmad,
            'SDLMIXER_SUPPORT_FLAC_MUSIC': self.options.with_flac,
            'SDLMIXER_SUPPORT_MODPLUG_MUSIC': self.options.with_libmodplug,
            'SDLMIXER_SUPPORT_MOD_MUSIC': self.options.with_libmikmod,
            'SDLMIXER_SUPPORT_MID_MUSIC_FLUIDSYNTH': False
        }
        src = os.path.join(self.conanfile_directory, self.folder)
        cmake.configure(build_dir='build', source_dir=src, defs=defs)
        cmake.build(target='install')

    # Deprecated for CMake
    def build_copying_libs(self):
        zip_name = "SDL2_mixer-devel-%s-VC.zip" % self.version
        download("https://www.libsdl.org/projects/SDL_mixer/release/%s" % zip_name, zip_name)
        unzip(zip_name)

    # Deprecated for CMake
    def build_with_make(self):
        
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        if self.options.fPIC:
            env_line = env.command_line.replace('CFLAGS="', 'CFLAGS="-fPIC ')
        else:
            env_line = env.command_line
        env_line = env.command_line.replace('LDFLAGS="', 'LDFLAGS="-Wl,--no-as-needed ')
            
        custom_vars = '' # Original: 'LIBPNG_LIBS= SDL_LIBS= LIBPNG_CFLAGS=' TODO SDL_VERSION
        sdl2_config_path = os.path.join(self.deps_cpp_info["SDL2"].lib_paths[0], "sdl2-config")
         
        self.run("cd %s" % self.folder)
        self.run("chmod a+x %s/configure" % self.folder)
        self.run("chmod a+x %s" % sdl2_config_path)
        
        configure_args = ["--disable-music-cmd", "--disable-music-mod-modplug", "--disable-music-mod-mikmod", "--disable-music-midi", # Stuff we give a shit about
                          "--disable-music-ogg", "--disable-music-flac", "--disable-music-mp3", # Stuff we declare broken atm
                          "--disable-sdltest", "--disable-smpegtest", ""] # We disable all manual tests
        self.output.warn(env_line)
        if self.settings.os == "Macos": # Fix rpath, we want empty rpaths, just pointing to lib file
            old_str = "-install_name \\$rpath/"
            new_str = "-install_name "
            replace_in_file("%s/configure" % self.folder, old_str, new_str)
        
        configure_command = 'cd %s && %s SDL2_CONFIG=%s %s ./configure %s' % (self.folder, env_line, sdl2_config_path, custom_vars, " ".join(configure_args))
        self.output.warn("Configure with: %s" % configure_command)
        self.run(configure_command)

        old_str = '\n# Commented by conan: CFLAGS ='
        fpic = "-fPIC"  if self.options.fPIC else ""
        m32 = "-m32" if self.settings.arch == "x86" else ""
        debug = "-g" if self.settings.build_type == "Debug" else "-s -DNDEBUG"
        new_str = '\nCFLAGS =%s %s %s %s\n# Commented by conan: CFLAGS =' % (" ".join(self.deps_cpp_info.cflags), fpic, m32, debug)
        replace_in_file("%s/Makefile" % self.folder, old_str, new_str)
        
        self.run("cd %s && %s make" % (self.folder, env_line))


    def package(self):
        """ Define your conan structure: headers, libs and data. After building your
            project, this method is called to create a defined structure:
        """
        folder = 'install'
        self.copy(pattern="*SDL_mixer.h", dst="include/SDL2", src=folder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=folder, keep_path=False)
        self.copy(pattern="*.dll*", dst="bin", src=folder, keep_path=False)
        self.copy(pattern="*.a", dst="lib", src=folder, keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=folder, keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", src=folder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["SDL2_mixer"]
        self.cpp_info.includedirs += ["include/SDL2"]
