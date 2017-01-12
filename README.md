[![Build Status](https://travis-ci.org/sixten-hilborn/conan-lua.svg?branch=master)](https://travis-ci.org/sixten-hilborn/conan-lua)
[![Build status](https://ci.appveyor.com/api/projects/status/clrxf3djdhnw0xr2?svg=true)](https://ci.appveyor.com/project/sixten-hilborn/conan-lua)

# conan-lua

[Conan.io](https://conan.io) package for lua library

## Build packages

Download conan client from [Conan.io](https://conan.io) and run:

    $ python build.py
    
## Upload packages to server

    $ conan upload lua/5.1.4@hilborn/stable --all
    
## Reuse the packages

### Basic setup

    $ conan install lua/5.1.4@hilborn/stable
    
### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*
    
    [requires]
    lua/5.1.4@hilborn/stable

    [options]
    lua:shared=True # False
    
    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:</small></span>

    mkdir build && cd build && conan install ..

Project setup installs the library (and all its dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.
