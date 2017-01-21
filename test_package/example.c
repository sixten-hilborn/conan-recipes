// Some example prog to test compile and link
#include <Cg/cg.h>

int main(int argc, char *argv[]) {
	CGcontext context = cgCreateContext();
	cgDestroyContext(context);
	return 0;
}