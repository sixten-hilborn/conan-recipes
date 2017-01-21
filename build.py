from conan.packager import ConanMultiPackager
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(pure_c=True)
    builder.builds = [[settings, options] for settings, options in builder.builds if not (platform.system() == "Linux" and settings["arch"] == "x86")]
    builder.run()

