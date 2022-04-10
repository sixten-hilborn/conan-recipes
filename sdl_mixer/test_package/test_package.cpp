#include <SDL.h>
#include <SDL_mixer.h>
#include <iostream>
#include <cstdlib>

void try_load(const char* file)
{
	if (Mix_Music* music = Mix_LoadMUS(file))
		Mix_FreeMusic(music);
	else
	{
		std::cerr << "Unable to open file '" << file << "': " << Mix_GetError() << std::endl;
		std::exit(1);
	}
}

int try_sdl_mixer()
{
	if (SDL_Init(SDL_INIT_AUDIO) != 0)
	{
		std::cerr << "Unable to initialize SDL: " << SDL_GetError() << std::endl;
		return 1;
	}
	if (Mix_OpenAudio(22050, MIX_DEFAULT_FORMAT, 2, 4096) != 0)
	{
		std::cerr << "Mix_OpenAudio: " << Mix_GetError() << std::endl;
		return 1;
	}

	try_load("test.wav");
	try_load("test.mp3");
	try_load("1_rosann.mid");

	Mix_CloseAudio();
	SDL_Quit();
	return 0;
}


int main(int argc, char** args)
{
	std::cout << "Compile, link and run successfully" << std::endl;
	return 0;
	// return try_sdl_mixer();
}