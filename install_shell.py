#!/usr/bin/python3
#
# SPDX-FileCopyrightText: (C) 2021 Lazula <26179473+Lazula@users.noreply.github.com>
# SPDX-License-Identifier: GPL-3.0-or-later


import os
import requests
import logging
import subprocess

from os.path import join, abspath


def install_shell(init_source, shell_dir, name, location, shell_type, source_path="", install_subdir="", search_and_replace=[], postfix=""):
    """ Install a shell to the shell directory. Please note that this currently
        only supports text files, not binary.

        init_source: str
            The directory containing optinit.
        shell_dir: str
            The shell directory to install to.
        name: str
            The literal file name for the shell. Used for both finding local
            files if source_path is not provided and the final name for
            installation.
        shell_type: str
            Currently only used to determine whether to place at shell_dir or
            join(shell_dir, "original").
        location: str
            "remote" or "local"
            Remote files expect source_path to be a URL. Local files are assumed
            to be located at join(init_source, "shell", name) unless source_path
            is present.
        source_path: str
            For remote files, the remote URL to download using requests.get().
            For local files, override the default local location.
        install_subdir: str
            An optional subdirectory of shell_dir. Applied AFTER the modifier
            from shell_type. (shell_dir for normal shells, join(shell_dir,
            "original") for reverse shells)
        search_and_replace: list
            A 2-index list which will have each set of values passed to
            str.replace() for the file's text. Most commonly used to place
            REPLACEME_LHOST and REPLACEME_LPORT.
        postfix: str
            A literal string to be appended to the file data. Added after
            search_and_replace is applied.
    """

    # Check for invalid location or source_path value
    # Apply default source_path, if applicable
    if location == "local":
        if source_path:
            source_path = abspath(join(init_source, source_path))
        else:
            source_path = abspath(join(init_source, "shell", name))
    elif location == "remote":
        if not source_path:
            logging.error(f"No source path for remote shell \"{name}\"")
            return False
    else:
        logging.error(f"Invalid shell location \"{location}\"")
        return False

    # Apply default install_subdir
    if not install_subdir:
        install_subdir = ""

    # If install_subdir is a list, turn it into a path string
    if type(install_subdir) is list:
        install_subdir = join(*install_subdir)

    # Apply shell_type path modifier
    if shell_type == "reverse":
        install_subdir = join("original", install_subdir)

    # Ensure the installation path exists
    install_path = abspath(join(shell_dir, install_subdir))
    os.makedirs(install_path, exist_ok=True)

    # Create the final file path name
    install_name = abspath(join(install_path, name))

    logging.debug(f"Installing shell {name} from {source_path} to {install_name}")

    # Get file text from source path
    if location == "local":
        file_text = open(source_path).read()
    elif location == "remote":
        file_text = requests.get(source_path).text
    else:
        logging.error(f"location is no longer a valid value: {location}")
        return False

    # Process text replacement
    for entry in search_and_replace:
        file_text.replace(entry[0], entry[1])

    # Write final shell to output file
    with open(install_name, "w") as shell_file:
        shell_file.write(file_text)
        if postfix:
            shell_file.write(postfix)
        shell_file.close()

    return True


def install_shells(init_source, shell_dir, shell_params, local_only=False, ignore_errors=False):
    os.makedirs(join(shell_dir, "original"), exist_ok=True)

    for name, shell_data in shell_params.items():
        if shell_data.get("location") != "local" and local_only:
            logging.debug(f"Skipping non-local shell {name}")
            continue

        try:
            success = install_shell(init_source = init_source,
                                    shell_dir = shell_dir,
                                    name = name,
                                    location = shell_data["location"],
                                    shell_type = shell_data.get("shell_type"),
                                    source_path = shell_data.get("source_path"),
                                    install_subdir = shell_data.get("install_subdir"),
                                    search_and_replace = shell_data.get("search_and_replace", []),
                                    postfix = shell_data.get("postfix")
                                   )
        except KeyError as e:
            logging.error(f"Missing required shell parameter for {name}: {e}")
            success = False
        except requests.RequestException as e:
            logging.error(f"Encountered an error during a request while installing shell {name}: {e}")
            success = False

        if (not success) and (not ignore_errors):
            return 1

    return 0
