from conans import ConanFile, ConfigureEnvironment
from conans.tools import download, unzip, replace_in_file
import os

class Sdl2MixerConan(ConanFile):
    name = "SDL2_mixer"
    version = "2.0.1"
    description = "SDL2_mixer is a sample multi-channel audio mixer library."
    folder = "SDL2_mixer-%s" % version
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = (
        'shared=False',
        'fPIC=True'
    )
    generators = "cmake"
    requires = "SDL2/2.0.5@lasote/ci"
    url = "https://github.com/sixten-hilborn/conan-sdl2_mixer"
    license = "zlib License - https://opensource.org/licenses/Zlib"

    def config(self):
        del self.settings.compiler.libcxx

    def source(self):
        if self.settings.os == "Windows":
            return
        zip_name = "%s.tar.gz" % self.folder
        download("https://www.libsdl.org/projects/SDL_mixer/release/%s" % zip_name, zip_name)
        unzip(zip_name)

    def build(self):
        if self.settings.os == "Windows":
            self.build_copying_libs()
        else:
            self.build_with_make()

    def build_copying_libs(self):
        zip_name = "SDL2_mixer-devel-%s-VC.zip" % self.version
        download("https://www.libsdl.org/projects/SDL_mixer/release/%s" % zip_name, zip_name)
        unzip(zip_name)

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
        
        configure_args = ["--disable-music-cmd", "--disable-music-mod-modplug", "--disable_music_mod_mikmod", "--disable-music-midi", # Stuff we give a shit about
                          "--disable-music-ogg", "--disable-music-flac", "--disable-music-mp3", # Stuff we declare broken atm
                          "--disable_sdltest", "--disable_smpegtest", ""] # We disable all manual tests
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
        self.copy(pattern="*SDL_mixer.h", dst="include/SDL2", src="%s" % self.folder, keep_path=False)

        if self.settings.os == "Windows":
            if self.settings.arch == "x86":
                self.copy(pattern="*.lib", dst="lib", src="%s/lib/x86" % self.folder, keep_path=False)
                self.copy(pattern="*.dll*", dst="bin", src="%s/lib/x86" % self.folder, keep_path=False)
            else:
                self.copy(pattern="*.lib", dst="lib", src="%s/lib/x64" % self.folder, keep_path=False)
                self.copy(pattern="*.dll*", dst="bin", src="%s/lib/x64" % self.folder, keep_path=False)
        if not self.options.shared:
            self.copy(pattern="*.a", dst="lib", src="%s" % self.folder, keep_path=False)
        else:
            self.copy(pattern="*.so*", dst="lib", src="%s" % self.folder, keep_path=False)
            self.copy(pattern="*.dylib*", dst="lib", src="%s" % self.folder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["SDL2_mixer"]
        self.cpp_info.includedirs += ["include/SDL2"]
