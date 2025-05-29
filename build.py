#!/usr/bin/env python
import os
import sys
import argparse
import yaml
from glob import glob
import subprocess

USER = "sixten-hilborn"
CHANNEL = "stable"


def main():
    args = parse_args()
    root_dir = os.path.dirname(os.path.realpath(__file__))
    dirs = glob(f"{root_dir}/*/")

    packages = []

    #conan_profile = os.getenv('CONAN_PROFILE')
    if args.dry_run:
        os.environ["CONAN_USER_HOME"] = os.path.join(root_dir, "conanhome")
        os.environ["CONAN_USER_HOME_SHORT"] = os.path.join(root_dir, "conanhome")

    for p in dirs:
        if os.path.isfile(f'{p}/config.yml'):
            packages.extend(load_config(p))
        elif os.path.isfile(f'{p}/conanfile.py'):
            packages.append((p, None))

    if not args.no_export:
        for path, version in packages:
            command = ["conan", "export", "--user", USER, "--channel", CHANNEL]
            if version is not None:
                command.extend(["--version", version])
            command.append(path)
            run_command(args, command)

    if args.build:
        for path, version in packages:
            command = ["conan", "create", "-b=missing", "--user", USER, "--channel", CHANNEL]
            if version is not None:
                command.extend(["--version", version])
            command.append(path)
            run_command(args, command)


def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-b', '--build', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--no-export', action='store_true')
    return parser.parse_args()


def load_config(path):
    with open(f'{path}/config.yml') as conf_file:
        config = yaml.load(conf_file, Loader=yaml.CLoader)
    packages = []
    versions = config['versions']
    for version, conf in versions.items():
        folder = conf['folder']
        packages.append((f"{path}/{folder}", f"{version}"))
    return packages


def run_command(args, command):
    command_str = ' '.join(command)
    try:
        if args.verbose:
            print(f"Running: '{command_str}'", file=sys.stderr)
        subprocess.run(command).check_returncode()
    except:
        print(f"Error while executing: '{command_str}'", file=sys.stderr)
        raise


if __name__ == '__main__':
    main()
