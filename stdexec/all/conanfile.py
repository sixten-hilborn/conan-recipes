from conans import ConanFile, tools


class StdexecRecipe(ConanFile):
    name = "stdexec"
    description = "`std::execution`, the proposed C++ framework for asynchronous and parallel programming."
    author = "Michał Dominiak, Lewis Baker, Lee Howes, Kirk Shoop, Michael Garland, Eric Niebler, Bryce Adelstein Lelbach"
    topics = ("WG21", "concurrency")
    homepage = "https://github.com/NVIDIA/stdexec"
    url = "https://github.com/sixten-hilborn/conan-recipes"
    license = "Apache 2.0"
    settings = "compiler", "os"  # Header only - compiler and os only used for flags

    def validate(self):
        tools.check_min_cppstd(self, "20")

    def package_id(self):
        # header only
        self.info.clear()

    def build_requirements(self):
        self.test_requires("catch2/2.13.6")

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True
        )

    def package(self):
        self.copy("*.hpp", dst="include", src=f"{self.source_folder}/include")

    def package_info(self):
        if self.settings.compiler == "gcc":
            self.cpp_info.cxxflags = ["-fcoroutines", "-fconcepts-diagnostics-depth=10"]
        elif self.settings.compiler == "Visual Studio":
            self.cpp_info.cxxflags = ["/Zc:__cplusplus", "/Zc:preprocessor"]

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
