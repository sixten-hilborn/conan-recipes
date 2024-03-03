#!/usr/bin/env python
import os
import sys
import argparse
import yaml
from glob import glob
import subprocess

REFERENCE = "sixten-hilborn/stable"


def main():
    args = parse_args()
    root_dir = os.path.dirname(os.path.realpath(__file__))
    dirs = glob(f"{root_dir}/*/")

    packages = []

    #conan_profile = os.getenv('CONAN_PROFILE')
    if args.dry_run:
        os.environ["CONAN_USER_HOME"] = os.path.join(root_dir, "conanhome")

    for p in dirs:
        if os.path.isfile(f'{p}/config.yml'):
            packages.extend(load_config(p))
        elif os.path.isfile(f'{p}/conanfile.py'):
            packages.append((p, REFERENCE))

    for path, ref in packages:
        run_command(["conan", "export", path, ref])

    if args.build:
        for path, ref in packages:
            run_command(["conan", "create", path, ref, "-k", "-b=outdated"])


def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-b', '--build', action='store_true')
    return parser.parse_args()


def load_config(path):
    with open(f'{path}/config.yml') as conf_file:
        config = yaml.load(conf_file, Loader=yaml.CLoader)
    packages = []
    versions = config['versions']
    for version, conf in versions.items():
        folder = conf['folder']
        packages.append((f"{path}/{folder}", f"{version}@{REFERENCE}"))
    return packages


def run_command(args):
    try:
        subprocess.run(args)
    except:
        command = ' '.join(args)
        print(f"Error while executing: '{command}'", file=sys.stderr)
        raise


if __name__ == '__main__':
    main()
