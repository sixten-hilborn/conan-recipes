#!/bin/bash -ex

if [ -f /Library/Frameworks/Cg.framework/Versions/1.0/Cg ]; then
    echo "Cg is already installed" >&2
    exit 0
fi

sudo hdiutil attach Cg.dmg
installer_path="/Volumes/Cg-3.1.0013/Cg-3.1.0013.app/Contents/Resources/Installer Items"
sudo cp "$installer_path/NVIDIA_Cg.tgz" /
sudo sh "$installer_path/install.sh" /
sudo hdiutil detach /Volumes/Cg-3.1.0013
