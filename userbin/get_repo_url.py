#!/usr/bin/python3

import argparse
import os
import sys
import subprocess
import json

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, help="The directory name to get a repository URL from. Provide ALL to search all directories.")
    parser.add_argument("-c", "--csv", action="store_true", help="Use CSV output instead of JSON.")
    return parser.parse_args()


def check_for_repository(basedir, dirname):
    os.chdir(os.path.join(basedir, dirname))
    proc = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True)
    remote_url = proc.stdout.decode().rstrip()
    return remote_url


def scan_repositories(basedir, repo_name=None, all_subdirs=False):
    if (not repo_name and not all_subdirs) or (repo_name and all_subdirs):
        raise ValueError("Must provide either repo_name or all_subdirs.")

    init_source = os.getcwd()
    basedir = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), "../"))

    if repo_name:
        repo_url = check_for_repository(basedir, repo_name)
        return {repo_name: repo_url}
    else:
        repo_data = {}
        with os.scandir(basedir) as entries:
            for entry in entries:
                if entry.is_dir():
                    repo_url = check_for_repository(basedir, entry.name)
                    if repo_url:
                        repo_data[entry.name] = repo_url
        return repo_data

    os.chdir(init_source)


def main(args):
    basedir = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), "../"))
    if args.name == "ALL":
        repo_data = scan_repositories(basedir, all_subdirs=True)
    else:
        repo_data = scan_repositories(basedir, repo_name=args.name)

    if args.csv:
        for repo_name, repo_url in repo_data.items():
            print(repo_name, repo_url, sep=",")
    else:
        print(json.dumps(repo_data, indent=4))

    return 0


if __name__ == "__main__":
    sys.exit(main(parse_arguments()))
