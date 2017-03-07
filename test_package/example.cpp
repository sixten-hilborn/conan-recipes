#include <CEGUI/CEGUI.h>
#include <iostream>

int main(int argc, char *argv[])
{
	std::cout
		<< "CEGUI version:" << std::endl
		<< CEGUI::System::getVerboseVersion().c_str() << std::endl;
	return 0;
}
