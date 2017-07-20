from conan.packager import ConanMultiPackager
from conans.tools import os_info

if __name__ == "__main__":
    builder = ConanMultiPackager(args='--build=missing')
    builder.add_common_builds(shared_option_name="smpeg:shared", pure_c=False)

    # Some isues with macOS/Linux and x86
    if os_info.is_linux or os_info.is_macos:
        filtered_builds = []
        for settings, options, env_vars, build_requires in builder.builds:
            if settings["arch"] != "x86":
                filtered_builds.append([settings, options, env_vars, build_requires])
        builder.builds = filtered_builds

    builder.run()
