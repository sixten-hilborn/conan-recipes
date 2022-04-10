cmake_minimum_required (VERSION 3.1.0)

project (SMPEG)

include(../conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(SMPEG_AUDIO_SRC
	audio/MPEGaudio.cpp
	audio/bitwindow.cpp
	audio/filter.cpp
	audio/filter_2.cpp
	audio/hufftable.cpp
	audio/mpeglayer1.cpp
	audio/mpeglayer2.cpp
	audio/mpeglayer3.cpp
	audio/mpegtable.cpp
	audio/mpegtoraw.cpp
)

set(SMPEG_VIDEO_SRC
	video/MPEGvideo.cpp
	video/decoders.cpp
	video/floatdct.cpp
	video/gdith.cpp
	video/jrevdct.cpp
	video/motionvec.cpp
	video/parseblock.cpp
	video/readfile.cpp
	video/util.cpp
	video/video.cpp
)

set(SMPEG_SRC
	MPEG.cpp
	MPEGlist.cpp
	MPEGring.cpp
	MPEGstream.cpp
	MPEGsystem.cpp
	smpeg.cpp
)

set(SMPEG_SOURCES
	${SMPEG_SRC}
	${SMPEG_AUDIO_SRC}
	${SMPEG_VIDEO_SRC}
)

set(SMPEG_CONTROLS OFF CACHE BOOL "Embeed media player controls")

if(NOT SMPEG_CONTROLS)
	add_definitions(-DNOCONTROLS)
endif()

include_directories("${SMPEG_SOURCE_DIR}")

add_library(smpeg2
	${SMPEG_SOURCES}
)

set_target_properties(smpeg2
    PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

if(WIN32)
	if(MSVC)
		#add_definitions(-DDECLSPEC="_declspec(dllexport)")
	endif()
endif()

target_link_libraries(smpeg2 PUBLIC CONAN_PKG::sdl)

if(CMAKE_COMPILER_IS_GNUCC AND NOT CMAKE_CXX_COMPILER_VERSION VERSION_LESS 6.0)
	target_compile_options(smpeg2 PRIVATE -Wno-narrowing)
endif()

if(CMAKE_CXX_COMPILER_ID MATCHES "Clang" AND NOT CMAKE_CXX_COMPILER_VERSION VERSION_LESS 6.0)
    target_compile_options(smpeg2 PRIVATE -Wno-c++11-narrowing)
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY build)

install(TARGETS smpeg2
	RUNTIME DESTINATION bin
	LIBRARY DESTINATION lib
	ARCHIVE DESTINATION lib)
install(DIRECTORY . DESTINATION include FILES_MATCHING PATTERN "*.h")