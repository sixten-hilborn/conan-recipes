from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import get, copy, replace_in_file
from conan.tools.build import check_min_cppstd


class StdexecRecipe(ConanFile):
    name = "stdexec"
    description = "`std::execution`, the proposed C++ framework for asynchronous and parallel programming."
    author = "Michał Dominiak, Lewis Baker, Lee Howes, Kirk Shoop, Michael Garland, Eric Niebler, Bryce Adelstein Lelbach"
    topics = ("WG21", "concurrency")
    homepage = "https://github.com/NVIDIA/stdexec"
    url = "https://github.com/sixten-hilborn/conan-recipes"
    license = "Apache 2.0"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "header-library"
    options = {
        "asio": [None, "boost", "standalone"],
    }
    default_options = {
        "asio": None,
    }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "20")

    def package_id(self):
        # header only
        self.info.settings.clear()

    def build_requirements(self):
        #self.test_requires("catch2/2.13.10")
        pass

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["STDEXEC_BUILD_TESTS"] = False
        if self.options.asio:
            tc.variables["STDEXEC_ENABLE_ASIO"] = True
            tc.variables["STDEXEC_ASIO_IMPLEMENTATION"] = self.options.asio
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        copy(self, "*.hpp", dst=f"{self.package_folder}/include", src=f"{self.source_folder}/include")

    def package_info(self):
        if self.settings.compiler == "gcc":
            self.cpp_info.cxxflags = ["-fcoroutines", "-fconcepts-diagnostics-depth=10"]
        elif self.settings.compiler == "msvc":
            self.cpp_info.cxxflags = ["/Zc:__cplusplus", "/Zc:preprocessor"]

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
