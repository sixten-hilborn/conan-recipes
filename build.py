#!/usr/bin/env python3
import os
from glob import glob


def system(command):
    retcode = os.system(command)
    if retcode != 0:
        raise Exception("Error while executing:\n\t %s" % command)


dirs = glob("./*/")

packages = []

conan_profile = os.getenv('CONAN_PROFILE')

for p in dirs:
    path = f'{p}/conanfile.py'
    if not os.path.isfile(path):
        continue
    packages.append(f"{p} sixten-hilborn/stable")

for pkg in packages:
    system(f"conan export {pkg}")

for pkg in packages:
    system(f"conan create {pkg} -k -b=outdated")
