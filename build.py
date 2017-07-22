from conan.packager import ConanMultiPackager
from conans.tools import os_info

if __name__ == "__main__":
    builder = ConanMultiPackager(args='--build=missing')
    builder.add_common_builds(shared_option_name="SDL2_mixer:shared", pure_c=True)

    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if settings["arch"] != "x86":
            filtered_builds.append([settings, options, env_vars, build_requires])
    builder.builds = filtered_builds

    builder.run()
