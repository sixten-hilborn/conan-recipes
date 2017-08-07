cmake_minimum_required(VERSION 2.8)
project(TestSDL_gpu)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(VERBOSE 1)
set(CMAKE_VERBOSE_MAKEFILE 1)

add_executable(example main.c)
conan_target_link_libraries(example)
