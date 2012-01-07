cmake_minimum_required(VERSION 2.8)
project(qibuild-cpp CXX)
find_package(qibuild)
enable_testing()

add_subdirectory(libqibuild)
add_subdirectory(gui)

