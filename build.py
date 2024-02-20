#!/usr/bin/env python
import os
import argparse
from glob import glob

def main():
    args = parse_args()
    root_dir = os.path.dirname(os.path.realpath(__file__))
    dirs = glob(f"{root_dir}/*/")

    packages = []

    #conan_profile = os.getenv('CONAN_PROFILE')
    if args.dry_run:
        os.environ["CONAN_USER_HOME"] = os.path.join(root_dir, "conanhome")

    for p in dirs:
        path = f'{p}/conanfile.py'
        if not os.path.isfile(path):
            continue
        packages.append(f"{p} sixten-hilborn/stable")

    for pkg in packages:
        system(f"conan export {pkg}")

    if args.build:
        for pkg in packages:
            system(f"conan create {pkg} -k -b=outdated")


def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-b', '--build', action='store_true')
    return parser.parse_args()


def system(command):
    retcode = os.system(command)
    if retcode != 0:
        raise Exception("Error while executing:\n\t %s" % command)


if __name__ == '__main__':
    main()
