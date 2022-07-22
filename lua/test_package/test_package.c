// The hello program
#include <stdio.h>
#include <lua.h>
#include <lualib.h>
#include <lauxlib.h>

int main(int argc, char *argv[]) {
	// Open lua
	lua_State *L = lua_open();

	// Load the libraries
	luaL_openlibs(L);

	// Execution of a lua string
	luaL_dostring(L, "print \"Testing dostring\"");

	// Load a string and then execute it.
	luaL_loadstring(L, "io.write(\"Testing loadstring\\n\")");
	lua_pcall(L, 0, LUA_MULTRET, 0);

	// Load from a file and then execute
	if (luaL_loadfile(L, "hello.lua") == 0) {
		// File loaded call it
		lua_pcall(L, 0, LUA_MULTRET, 0);
	} else {
		printf("Unable to load file hello.lua\n");
	}

	// Close lua
	lua_close(L);

	return 0;
}