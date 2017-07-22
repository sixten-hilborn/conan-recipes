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


int main(int argc, char** args)
{
	SDL_Init(SDL_INIT_EVERYTHING);
	Mix_OpenAudio(22050, MIX_DEFAULT_FORMAT, 2, 4096);

	try_load("test.wav");
	try_load("test.mp3");
	try_load("1_rosann.mid");

	Mix_CloseAudio();
	SDL_Quit();

	return 0;
}