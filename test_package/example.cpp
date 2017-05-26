#include <SDL.h>
#include <SDL_mixer.h>


int main(int argc, char** args)
{
	SDL_Init(SDL_INIT_EVERYTHING);
	Mix_OpenAudio(22050, MIX_DEFAULT_FORMAT, 2, 4096);

	Mix_Music* music = Mix_LoadMUS("test.wav");
	Mix_FreeMusic(music);
	Mix_CloseAudio();
	SDL_Quit();

	return 0;
}