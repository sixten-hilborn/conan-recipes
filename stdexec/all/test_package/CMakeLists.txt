project(test_package)
cmake_minimum_required(VERSION 3.17)

find_package(Threads REQUIRED)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS} Threads::Threads)
