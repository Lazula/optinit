#!/usr/bin/python3
#
# optinit.py Copyright (C) Lazula 2021
# Distributed under GNU GPLv3 or later
# Further license information at end of file

import argparse
import os
import sys
import shutil
import logging
import errno
import subprocess
import json

import install_bin
import install_shell

def parse_arguments():
    parser = argparse.ArgumentParser(description="Install a set of tools and custom scripts to a given directory. If it does not exist, attempt to create it before installing.")
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    verbosity.add_argument("-q", "--quiet", action="store_true", help="Display only essential output.")
    parser.add_argument("-d", "--install-dir", type=str, required=True, help="The installation directory.")
    parser.add_argument("-i", "--ignore-errors", action="store_true", help="Do not exit on recoverable error.")
    parser.add_argument("-l", "--local-only", action="store_true", help="Install only the userbin. Disables all remote downloads.")
    parser.add_argument("-u", "--update", action="store_true", help="Update an existing installation.")
    parser.add_argument("-a", "--archive-userbin", action="store_true", help="Move all current userbin files into an archive subdirectory. No effect if run without --update.")
    configs = parser.add_argument_group()
    configs.add_argument("-r", "--repository-config-file", type=str, default="repositories.txt", help="Specify repository file location.")
    configs.add_argument("-b", "--binary-config-file", type=str, default="binaries.txt", help="Specify binary configuration file location.")
    return parser.parse_args()


def prepare_install_dir(install_dir, userbin_only=False):
    try:
        os.makedirs(install_dir)
        logging.debug(f"Created {install_dir}.")
    except FileExistsError:
        logging.debug(f"{install_dir} already exists.")
        if not os.path.isdir(install_dir):
            logging.error(f"{install_dir} is not a directory.")
            return errno.ENOTDIR
        if not os.access(install_dir, os.W_OK):
            logging.error(f"No write permissions in {install_dir}.")
            return errno.EACCES
    except PermissionError:
        logging.error(f"Could not create {install_dir}.")
        return errno.EPERM

    userbin_dir = os.path.join(install_dir, "userbin")
    try:
        os.makedirs(userbin_dir)
        logging.debug(f"Created {userbin_dir}.")
    except FileExistsError:
        logging.debug(f"{userbin_dir} already exists.")

    if userbin_only:
        return 0

    bin_dir = os.path.join(install_dir, "bin")
    try:
        os.makedirs(bin_dir)
        logging.debug(f"Created {bin_dir}.")
    except FileExistsError:
        logging.debug(f"{bin_dir} already exists.")

    logging.debug(f"{install_dir} ready for install.")
    return 0


def get_existing_repositories(init_source, install_dir):
    """ Return a dictionary that maps existing repository URLS to directory
        names. Skips over non-repository directories.
    """

    existing_repositories = {}

    # Documentation advises explicit use of with when using os.scandir()
    with os.scandir(install_dir) as entries:
        for entry in entries:
            if entry.is_dir():
                os.chdir(os.path.join(install_dir, entry.name))
                proc = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True)
                remote_url = proc.stdout.decode().rstrip()
                # remote_url is empty if the directory is not a git repo
                if len(remote_url) > 0:
                    existing_repositories[remote_url] = entry.name

    os.chdir(init_source)

    return existing_repositories


def install_repositories(init_source, install_dir, repository_file, update=False, ignore_errors=False):
    """ Install or update repositories.

        If updating, move existing repositories if they should be renamed.
    """

    if update:
        logging.info("Updating repositories.")
    else:
        logging.info("Installing repositories.")

    if update:
        existing_repositories = get_existing_repositories(init_source, install_dir)
    else:
        existing_repositories = {}

    entries = json.load(open(repository_file, "r"))

    for repo_name, repo_url in entries.items():
        try:
            # If the repository URL doesn't exist, it hasn't been installed yet
            old_name = existing_repositories[repo_url]
            if repo_name != old_name:
                logging.debug(f"Moving {old_name} to {repo_name}.")
                shutil.move(os.path.join(install_dir, old_name), os.path.join(install_dir, repo_name))

            logging.debug(f"Updating {repo_name}.")
            os.chdir(os.path.join(install_dir, repo_name))
            try:
                subprocess.run(["git", "pull", "--ff-only"], stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                logging.error(f"An error was encountered while updating {repo_name}.")
                if not ignore_errors:
                    return e.returncode
        except KeyError:
            # Repository needs to be installed
            logging.debug(f"Cloning {repo_name}")
            os.chdir(install_dir)
            try:
                subprocess.run(["git", "clone", repo_url, repo_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                logging.error(f"An error was encountered while cloning {repo_name}.")
                if not ignore_errors:
                    return e.returncode

    os.chdir(init_source)
    return 0


def install_scripts(init_source, userbin_dir, update=False, archive_old_files=True):
    userbin_source = os.path.join(init_source, "userbin")
    if update:
        if archive_old_files:
            logging.debug(f"Archiving userbin files.")
            shutil.copytree(userbin_source, os.path.join(userbin_dir, "userbin_archive"), dirs_exist_ok=True)
        else:
            logging.debug(f"userbin files will not be archived.")
    shutil.copytree(userbin_source, userbin_dir, dirs_exist_ok=True)


def install(init_source, install_dir, repository_file, binary_params, local_only=False, update=False, ignore_errors=False, archive_userbin=False):
    status = prepare_install_dir(install_dir, userbin_only=local_only)
    # None of the nonzero error codes here are recoverable
    if status:
        return status

    userbin_dir = os.path.join(install_dir, "userbin")
    logging.info(f"Copying scripts to {userbin_dir}")
    status = install_scripts(init_source, userbin_dir=userbin_dir, update=update, archive_old_files=archive_userbin)
    if status:
        return status

    if local_only:
        logging.debug(f"local_only enabled. Installation complete.")
        # Create a file to mark the installation as completed
        with open(os.path.join(install_dir, ".optinit"), "w") as _:
            pass

    logging.debug(f"local_only disabled. Continuing installation.")
    binary_dir = os.path.join(install_dir, "bin")
    download_log_file = os.path.join(binary_dir, ".download_log")
    try:
        download_log = json.load(open(download_log_file, "r"))
    except FileNotFoundError:
        download_log = {}
    logging.info(f"Downloading static binaries to {binary_dir}")
    install_bin.install_binaries(binary_dir=binary_dir, binary_params=binary_params, download_log=download_log, ignore_errors=ignore_errors)
    json.dump(download_log, open(download_log_file, "w"))
    if status:
        return status

    status = install_repositories(init_source, install_dir, repository_file, update=update, ignore_errors=ignore_errors)
    if status:
        logging.error(f"Returning child error code.")
        return status

    install_shell.install_shell(install_dir, ignore_errors=ignore_errors)

    # Copy READMEs
    logging.debug("Copying READMEs")
    for directory in ["bin", "userbin", "shell"]:
        shutil.copy2(os.path.join(init_source, "directory_readmes", f"{directory}.md"), os.path.join(install_dir, directory, "README.md"))

    # Create a file to mark the installation as completed
    with open(os.path.join(install_dir, ".optinit"), "w") as _:
        pass

    logging.info("Installation complete.")


def main(args):
    if args.quiet:
        logging.disable()
    elif args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

    # Forcibly disable urllib3 debug output
    logging.getLogger("urllib3").setLevel(logging.INFO)

    init_source = os.getcwd()
    install_dir = os.path.join(init_source, args.install_dir)
    repository_file = os.path.join(init_source, args.repository_config_file)
    binary_config_file = os.path.join(init_source, args.binary_config_file)
    try:
        binary_params = json.load(open(binary_config_file, "r"))
    except FileNotFoundError:
        logging.error(f"{binary_config_file} does not exist.")
        if not args.ignore_errors:
            return 1
        binary_params = {}
    except json.decoder.JSONDecodeError as e:
        logging.error(f"Error in binary config file format: {e}")
        if not args.ignore_errors:
            return 1

    if not os.access(repository_file, os.F_OK) and not args.ignore_errors:
        logging.error(f"{repository_file} does not exist.")
        return 1

    try:
        if os.access(os.path.join(install_dir, ".optinit"), os.F_OK) and not args.update:
            logging.error(f"An existing installation exists. Run with -u if you would like to update it (add -a to archive the current userbin contents). No further action will be taken at this time.")
            return 1
        else:
            status = install(init_source, install_dir, repository_file, binary_params, local_only=args.local_only, update=args.update, ignore_errors=args.ignore_errors, archive_userbin=args.archive_userbin)
    except KeyboardInterrupt:
        os.chdir(init_source)
        logging.info(f"Caught keyboard interrupt. Exiting.")
        sys.exit(1)

    try:
        if status:
            logging.error(os.strerror(status))
    except ValueError:
        logging.error(f"Cannot convert error code {status} to a message.")

    return status


if __name__ == "__main__":
    sys.exit(main(parse_arguments()))


""" This file is part of optinit.

    optinit is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    optinit is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with optinit.  If not, see <https://www.gnu.org/licenses/>.
"""
