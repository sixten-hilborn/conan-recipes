from conan.packager import ConanMultiPackager
from conans.tools import os_info
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name="CEGUI:shared", pure_c=False)

    extra_options = []
    if os_info.is_macos:
        extra_options += [("CEGUI:with_ois", "False"), ("CEGUI:with_sdl", "True")]  # Build with SDL since OIS doesn't work on macOS
    # Disable VS2010 because of missing DirectX stuff
    # Disable x86 Linux builds (OGRE x86 package does not work at the moment)
    builder.builds = [
        [settings, dict(options.items() + extra_options), env_vars, build_requires]
        for settings, options, env_vars, build_requires in builder.builds
        if not (settings["compiler"] == "Visual Studio" and settings["compiler.version"] == "10")
        and not (os_info.is_linux and settings["arch"] == "x86")
    ]
    builder.run()

