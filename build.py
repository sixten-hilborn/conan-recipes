from conan.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name="lua:shared", pure_c=True, dll_with_static_runtime=True)
    builder.run()

