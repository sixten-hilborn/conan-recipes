project(test_package)
cmake_minimum_required(VERSION 2.8.11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
configure_file(1_rosann.mid 1_rosann.mid COPYONLY)
configure_file(test.wav test.wav COPYONLY)
configure_file(test.mp3 test.mp3 COPYONLY)
