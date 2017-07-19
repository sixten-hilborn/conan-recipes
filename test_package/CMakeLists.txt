cmake_minimum_required(VERSION 2.8)
project(TestSmpeg)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(VERBOSE 1)
set(CMAKE_VERBOSE_MAKEFILE 1)

add_executable(example example.cpp)
conan_target_link_libraries(example)
