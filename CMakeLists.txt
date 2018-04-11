cmake_minimum_required (VERSION 3.1.0)
project (SDL2_mixer)

#list(APPEND CMAKE_MODULE_PATH "${SDLMIXER_SOURCE_DIR}/cmake")

#include(CheckSymbolExists)
#include(CheckLibraryExists)
#include(CheckIncludeFiles)
#include(CheckIncludeFile)

include(../conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(SDLMIXER_LIBRARIES "")

if (WIN32)
	set(SDLMIXER_SUPPORT_CMD_MUSIC OFF CACHE BOOL "Support for external command for playing music")
	set(SDLMIXER_SUPPORT_WAV_MUSIC ON CACHE BOOL "Support for WAV music")
	set(SDLMIXER_SUPPORT_MOD_MODPLUG_MUSIC OFF CACHE BOOL "Support for ModPlug music")
	set(SDLMIXER_SUPPORT_MOD_MIDKMOD_MUSIC OFF CACHE BOOL "Support for Mod music")
	set(SDLMIXER_SUPPORT_MID_MUSIC ON CACHE BOOL "Support for MIDI music")
		set(SDLMIXER_SUPPORT_MID_MUSIC_TIMIDITY ON CACHE BOOL "Support for MIDI over TIMIDITI music")
		set(SDLMIXER_SUPPORT_MID_MUSIC_FLUIDSYNTH OFF CACHE BOOL "Support for MIDI over FluidSynth music")
		set(SDLMIXER_SUPPORT_MID_MUSIC_NATIVE ON CACHE BOOL "Support for native MIDI music")
	set(SDLMIXER_SUPPORT_OGG_MUSIC ON CACHE BOOL "Support for OggVorbis music")
	set(SDLMIXER_SUPPORT_MP3_SMPEG_MUSIC OFF CACHE BOOL "Support for MP3 smpeg2 music")
	set(SDLMIXER_SUPPORT_MP3_MPG123_MUSIC ON CACHE BOOL "Support for MP3 mpg123 music")
	set(SDLMIXER_SUPPORT_MP3_MAD_MUSIC OFF CACHE BOOL "Support for MP3 MAD music")
	set(SDLMIXER_SUPPORT_FLAC_MUSIC ON CACHE BOOL "Support for FLAC music")
else()
	set(SDLMIXER_SUPPORT_CMD_MUSIC ON CACHE BOOL "Support for external command for playing music")
	set(SDLMIXER_SUPPORT_WAV_MUSIC ON CACHE BOOL "Support for WAV music")
	set(SDLMIXER_SUPPORT_MOD_MODPLUG_MUSIC ON CACHE BOOL "Support for ModPlug music")
	set(SDLMIXER_SUPPORT_MOD_MIDKMOD_MUSIC ON CACHE BOOL "Support for Mod music")
	set(SDLMIXER_SUPPORT_MID_MUSIC ON CACHE BOOL "Support for MIDI music")
		set(SDLMIXER_SUPPORT_MID_MUSIC_TIMIDITY ON CACHE BOOL "Support for MIDI over TIMIDITI music")
		set(SDLMIXER_SUPPORT_MID_MUSIC_FLUIDSYNTH ON CACHE BOOL "Support for MIDI over FluidSynth music")
		if(APPLE)
			set(SDLMIXER_SUPPORT_MID_MUSIC_NATIVE ON CACHE BOOL "Support for native MIDI music")
		else()
			set(SDLMIXER_SUPPORT_MID_MUSIC_NATIVE OFF CACHE BOOL "Support for native MIDI music")
		endif()
	set(SDLMIXER_SUPPORT_OGG_MUSIC ON CACHE BOOL "Support for OggVorbis music")
	set(SDLMIXER_SUPPORT_MP3_SMPEG_MUSIC ON CACHE BOOL "Support for MP3 smpeg2 music")
	set(SDLMIXER_SUPPORT_MP3_MPG123_MUSIC ON CACHE BOOL "Support for MP3 mpg123 music")
	set(SDLMIXER_SUPPORT_MP3_MAD_MUSIC ON CACHE BOOL "Support for MP3 MAD music")
	set(SDLMIXER_SUPPORT_FLAC_MUSIC ON CACHE BOOL "Support for FLAC music")
endif()

if(SDLMIXER_SUPPORT_CMD_MUSIC)
	add_definitions(-DMUSIC_CMD)
endif()
if(SDLMIXER_SUPPORT_WAV_MUSIC)
	add_definitions(-DMUSIC_WAV)
endif()
if(SDLMIXER_SUPPORT_MOD_MODPLUG_MUSIC)
	add_definitions(-DMUSIC_MOD_MODPLUG)
	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::libmodplug)
endif()
if(SDLMIXER_SUPPORT_MOD_MIDKMOD_MUSIC)
	add_definitions(-DMUSIC_MOD_MIKMOD)
	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::libmikmod)
endif()

if(SDLMIXER_SUPPORT_MID_MUSIC)
	if(SDLMIXER_SUPPORT_MID_MUSIC_TIMIDITY)
		add_definitions(-DMUSIC_MID_TIMIDITY)
		include_directories(timidity)
		set(SDLMIXER_TIMIDITY_SRC
			timidity/common.c
			timidity/instrum.c
			timidity/mix.c
			timidity/output.c
			timidity/playmidi.c
			timidity/readmidi.c
			timidity/resample.c
			timidity/tables.c
			timidity/timidity.c
		)
		
		list(APPEND SDLMIXER_ADDITIONAL_SRC ${SDLMIXER_TIMIDITY_SRC})
	endif()
	if(SDLMIXER_SUPPORT_MID_MUSIC_NATIVE)
		add_definitions(-DMUSIC_MID_NATIVE)
		include_directories(native_midi)
		set(SDLMIXER_NATIVEMIDI_SRC
			native_midi/native_midi_common.c
		)
		if (WIN32)
			list(APPEND SDLMIXER_NATIVEMIDI_SRC native_midi/native_midi_win32.c)
			list(APPEND SDLMIXER_LIBRARIES winmm.lib)
		elseif(UNIX)
			if (APPLE)
				list(APPEND SDLMIXER_NATIVEMIDI_SRC native_midi/native_midi_macosx.c)
			endif()
		endif()
		
		list(APPEND SDLMIXER_ADDITIONAL_SRC ${SDLMIXER_NATIVEMIDI_SRC})
	endif()
endif()

if(SDLMIXER_SUPPORT_OGG_MUSIC)
	add_definitions(-DMUSIC_OGG)
	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::ogg)
	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::vorbis)
endif()

if(SDLMIXER_SUPPORT_MP3_SMPEG_MUSIC)
	add_definitions(-DMP3_MUSIC)
	add_definitions(-DMUSIC_MP3_SMPEG)
	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::smpeg2)
endif()

if(SDLMIXER_SUPPORT_MP3_MPG123_MUSIC)
	add_definitions(-DMUSIC_MP3_MPG123)
	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::mpg123)
endif()

if(SDLMIXER_SUPPORT_MP3_MAD_MUSIC)
	add_definitions(-DMUSIC_MP3_MAD)
	# GPL extensions?
	# add_definitions(-DMUSIC_MP3_MAD_GPL_DITHERING)

	if (("${CMAKE_SYSTEM_PROCESSOR}" MATCHES "x86_64|AMD64"))
		add_definitions(-DFPM_64BIT)
	elseif (("${CMAKE_SYSTEM_PROCESSOR}" MATCHES "x86"))
		add_definitions(-DFPM_INTEL)
	elseif (("${CMAKE_SYSTEM_PROCESSOR}" MATCHES "arm"))
		add_definitions(-DFPM_ARM)
	else()
		message("Unknown architecture: ${CMAKE_SYSTEM_PROCESSOR}")
	endif()

	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::libmad)
endif()

if(SDLMIXER_SUPPORT_FLAC_MUSIC)
	add_definitions(-DMUSIC_FLAC)
	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::flac)
endif()

include_directories(./)

add_library(SDL2_mixer
	effect_position.c
	effect_stereoreverse.c
	effects_internal.c
	load_aiff.c
	load_voc.c
	mixer.c
	music.c
	music_cmd.c
	music_flac.c
	music_fluidsynth.c
	music_mad.c
	music_mikmod.c
	music_modplug.c
	music_mpg123.c
	music_nativemidi.c
	music_ogg.c
	music_smpeg.c
	music_timidity.c
	music_wav.c
	${SDLMIXER_ADDITIONAL_SRC}
)
	
target_link_libraries(SDL2_mixer CONAN_PKG::sdl2 ${SDLMIXER_LIBRARIES})

install(TARGETS SDL2_mixer
	RUNTIME DESTINATION bin
	LIBRARY DESTINATION lib
	ARCHIVE DESTINATION lib)
install(FILES SDL_mixer.h DESTINATION include/SDL2)