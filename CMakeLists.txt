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
	set(SDLMIXER_SUPPORT_MODPLUG_MUSIC OFF CACHE BOOL "Support for ModPlug music")
	set(SDLMIXER_SUPPORT_MOD_MUSIC OFF CACHE BOOL "Support for Mod music")
	set(SDLMIXER_SUPPORT_MID_MUSIC ON CACHE BOOL "Support for MIDI music")
		set(SDLMIXER_SUPPORT_MID_MUSIC_TIMIDITY ON CACHE BOOL "Support for MIDI over TIMIDITI music")
		set(SDLMIXER_SUPPORT_MID_MUSIC_FLUIDSYNTH OFF CACHE BOOL "Support for MIDI over FluidSynth music")
		set(SDLMIXER_SUPPORT_MID_MUSIC_NATIVE ON CACHE BOOL "Support for native MIDI music")
	set(SDLMIXER_SUPPORT_OGG_MUSIC ON CACHE BOOL "Support for OggVorbis music")
	set(SDLMIXER_SUPPORT_MP3_MUSIC OFF CACHE BOOL "Support for MP3 music")
	set(SDLMIXER_SUPPORT_MP3_MAD_MUSIC OFF CACHE BOOL "Support for MP3 MAD music")
	set(SDLMIXER_SUPPORT_FLAC_MUSIC ON CACHE BOOL "Support for FLAC music")
else()
	set(SDLMIXER_SUPPORT_CMD_MUSIC ON CACHE BOOL "Support for external command for playing music")
	set(SDLMIXER_SUPPORT_WAV_MUSIC ON CACHE BOOL "Support for WAV music")
	set(SDLMIXER_SUPPORT_MODPLUG_MUSIC ON CACHE BOOL "Support for ModPlug music")
	set(SDLMIXER_SUPPORT_MOD_MUSIC ON CACHE BOOL "Support for Mod music")
	set(SDLMIXER_SUPPORT_MID_MUSIC ON CACHE BOOL "Support for MIDI music")
		set(SDLMIXER_SUPPORT_MID_MUSIC_TIMIDITY ON CACHE BOOL "Support for MIDI over TIMIDITI music")
		set(SDLMIXER_SUPPORT_MID_MUSIC_FLUIDSYNTH ON CACHE BOOL "Support for MIDI over FluidSynth music")
		if(APPLE)
			set(SDLMIXER_SUPPORT_MID_MUSIC_NATIVE ON CACHE BOOL "Support for native MIDI music")
		else()
			set(SDLMIXER_SUPPORT_MID_MUSIC_NATIVE OFF CACHE BOOL "Support for native MIDI music")
		endif()
	set(SDLMIXER_SUPPORT_OGG_MUSIC ON CACHE BOOL "Support for OggVorbis music")
	set(SDLMIXER_SUPPORT_MP3_MUSIC ON CACHE BOOL "Support for MP3 music")
	set(SDLMIXER_SUPPORT_MP3_MAD_MUSIC ON CACHE BOOL "Support for MP3 MAD music")
	set(SDLMIXER_SUPPORT_FLAC_MUSIC ON CACHE BOOL "Support for FLAC music")
endif()

if(SDLMIXER_SUPPORT_CMD_MUSIC)
	add_definitions(-DCMD_MUSIC)
endif()
if(SDLMIXER_SUPPORT_WAV_MUSIC)
	add_definitions(-DWAV_MUSIC)
endif()
if(SDLMIXER_SUPPORT_MODPLUG_MUSIC)
	add_definitions(-DMODPLUG_MUSIC)
	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::libmodplug)
endif()
if(SDLMIXER_SUPPORT_MOD_MUSIC)
	add_definitions(-DMOD_MUSIC)
	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::libmikmod)
endif()

if(SDLMIXER_SUPPORT_MID_MUSIC)
	add_definitions(-DMID_MUSIC)
	if(SDLMIXER_SUPPORT_MID_MUSIC_TIMIDITY)
		add_definitions(-DUSE_TIMIDITY_MIDI)
		include_directories(timidity)
		set(SDLMIXER_TIMIDITY_SRC
			timidity/common.c
			timidity/ctrlmode.c
			timidity/filter.c
			timidity/instrum.c
			timidity/mix.c
			timidity/output.c
			timidity/playmidi.c
			timidity/readmidi.c
			timidity/resample.c
			timidity/sdl_a.c
			timidity/sdl_c.c
			timidity/tables.c
			timidity/timidity.c
		)
		
		list(APPEND SDLMIXER_ADDITIONAL_SRC ${SDLMIXER_TIMIDITY_SRC})

	endif()
	if(SDLMIXER_SUPPORT_MID_MUSIC_FLUIDSYNTH)
		add_definitions(-DUSE_FLUIDSYNTH_MIDI)
	endif()
	if(SDLMIXER_SUPPORT_MID_MUSIC_NATIVE)
		add_definitions(-DUSE_NATIVE_MIDI)
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
	add_definitions(-DOGG_MUSIC)
	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::ogg)
	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::vorbis)
endif()

if(SDLMIXER_SUPPORT_MP3_MUSIC)
	add_definitions(-DMP3_MUSIC)
	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::smpeg)
endif()

if(SDLMIXER_SUPPORT_MP3_MAD_MUSIC)
	add_definitions(-DMP3_MAD_MUSIC)

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
	add_definitions(-DFLAC_MUSIC)
	list(APPEND SDLMIXER_LIBRARIES CONAN_PKG::flac)
endif()

include_directories(./)

add_library(SDL2_mixer
	dynamic_flac.c
	dynamic_fluidsynth.c
	dynamic_mod.c
	dynamic_modplug.c
	dynamic_mp3.c
	dynamic_ogg.c
	effect_position.c
	effect_stereoreverse.c
	effects_internal.c
	fluidsynth.c
	load_aiff.c
	load_flac.c
	load_mp3.c
	load_ogg.c
	load_voc.c
	mixer.c
	music.c
	music_cmd.c
	music_flac.c
	music_mad.c
	music_mod.c
	music_modplug.c
	music_ogg.c
	wavestream.c
	${SDLMIXER_ADDITIONAL_SRC})
	
target_link_libraries(SDL2_mixer CONAN_PKG::SDL2 ${SDLMIXER_LIBRARIES})

install(TARGETS SDL2_mixer
	RUNTIME DESTINATION bin
	LIBRARY DESTINATION lib
	ARCHIVE DESTINATION lib)
install(FILES SDL_mixer.h DESTINATION include/SDL2)