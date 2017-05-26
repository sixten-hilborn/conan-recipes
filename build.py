from conan.packager import ConanMultiPackager
from conans.tools import os_info

if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name="SDL2_mixer:shared", pure_c=True)

    # Some isues with macOS/Linux and x86
    if os_info.is_linux or os_info.is_macos:
        filtered_builds = []
        for settings, options, env_vars, build_requires in builder.builds:
            if settings["arch"] != "x86":
                filtered_builds.append([settings, options, env_vars, build_requires])
        builder.builds = filtered_builds

    builder.run()
