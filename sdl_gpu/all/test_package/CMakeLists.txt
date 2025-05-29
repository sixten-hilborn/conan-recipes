cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(SDL_gpu REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE SDL_gpu::SDL_gpu)
