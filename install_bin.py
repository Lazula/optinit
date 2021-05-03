#!/usr/bin/python3
#
# install_bin.py Copyright (C) Lazula 2021
# Distributed under GNU GPLv3 or later
# Further license information at end of file

import requests
import re
import logging
import hashlib
import os
import sys
import gzip
import json


class BadChecksumError(Exception):
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual
        self.message = f"Expected {expected}, got {actual}"


def get_listed_checksum(checksum_file_data, file_name, hash_type):
    """ Get a checksum from a standard-format checksum file (i.e. the hash is
        first on the line, followed by the file name with two spaces separating
        them.

        Raises a BadChecksumException if validation fails.

        Returns the checksum on success.
    """

    hash_regex = {
        "md5":    "([0-9a-f]{32})",
        "sha1":   "([0-9a-f]{40})",
        "sha256": "([0-9a-f]{64})",
        "sha512": "([0-9a-f]{128})",
    }

    try:
        match = re.search("  ".join([hash_regex[hash_type], file_name]), checksum_file_data)
    except KeyError:
        raise ValueError(f"Invalid hash type: {hash_type}")

    try:
        return match.group(1)
    except AttributeError:
        logging.warning(f"Failed to find {hash_type} checksum for {file_name}.")
        raise None


def download_and_verify_binary(name, download_url, expected_checksum, hash_type):
    """ Download a file using the given URL and verify its checksum. Supports
        MD5, SHA1, SHA256, and SHA512. Checksum must be in hexadecimal ASCII
        format.

        Returns the binary data in raw bytes form if the checksums match. Raises
        a BadChecksumError if they do not.
    """

    binary_data = requests.get(download_url).content
    if hash_type == "md5":
        real_checksum = hashlib.md5(binary_data).hexdigest()
    elif hash_type == "sha1":
        real_checksum = hashlib.sha1(binary_data).hexdigest()
    elif hash_type == "sha256":
        real_checksum = hashlib.sha256(binary_data).hexdigest()
    elif hash_type == "sha512":
        real_checksum = hashlib.sha512(binary_data).hexdigest()
    else:
        raise ValueError(f"Invalid hash type: {hash_type}")

    if expected_checksum == real_checksum:
        logging.debug(f"Successfully verified checksum for {name}.")
    else:
        raise BadChecksumError(expected=expected_checksum, actual=real_checksum)

    return binary_data


def install_binary(binary_dir, download_log, name, source_url_format, file_name_format, checksum_file_name_format=None, checksum_algorithm=None, release_version=None, use_gzip=False, arch="32", arch_strings=None):
    """ Install a binary to the binary directory.

        Format string arguments may contain other arguments such as the release
        version and architecture, as well as arch_string, the arch_strings entry
        for arch (if both exist).

        binary_dir
            The directory to write the downloaded file to.
        download_log
            A dictionary which holds the names and source URLs of installed
            binaries.
        name
            The file name used for the binary.
        source_url_format
            A format string used as the base download URL.
        file_name_format
            A format string used as the file name to download.
        checksum_file_name_format
            A format string used as the checksum file name.
        checksum_algorithm
            The algorithm to use when calculating the file's checksum.
        use_gzip
            Attempts to extract the downloaded file with gzip before writing its
            contents.
        arch
            A string that defines the architecture.
        arch_strings
            A dictionary which maps the arch to a string that can be used in
            the format strings.
    """

    try:
        arch_string = arch_strings[arch]
    except NameError:
        arch_string = ""
    except KeyError:
        raise ValueError(f"Invalid arch: {arch}. Must be one of: {list(arch_strings.keys())}")

    source_url = source_url_format.format(**locals())
    file_name = file_name_format.format(**locals())
    file_download_url = f"{source_url}/{file_name}"

    existing_install_url = download_log.get(name)
    if download_log.get(name) == file_download_url:
        logging.debug(f"Same {name} version already installed.")
        return True
    elif existing_install_url:
        logging.debug(f"Overwriting old {name} installation.")
    else:
        logging.debug(f"{name} not installed yet.")

    if checksum_file_name_format:
        checksum_file_name = checksum_file_name_format.format(**locals())
        checksum_file_url = f"{source_url}/{checksum_file_name}"

        expected_checksum = get_listed_checksum(requests.get(checksum_file_url).text, file_name, checksum_algorithm)
        if not expected_checksum:
            logging.debug(f"Could not extract checksum from {checksum_url}")
            return False

        try:
            file_binary_data = download_and_verify_binary(file_name, file_download_url, expected_checksum, hash_type=checksum_algorithm)
        except BadChecksumError as e:
            logging.error(f"Failed to verify checksum for {name}. Expected {expected_checksum}, got {real_checksum}. Aborting {name} installation.")
            return False
    else:
        file_binary_data = requests.get(file_download_url).content

    file_path = os.path.join(binary_dir, name)
    with open(file_path, "wb") as target_file:
        if use_gzip:
            file_binary_data = gzip.decompress(file_binary_data)
        target_file.write(file_binary_data)
    os.chmod(file_path, 0o755)
    download_log[name] = file_download_url
    logging.debug(f"Successfully installed {name}.")

    return True


def install_binaries(binary_dir, binary_params, download_log={}, ignore_errors=False):
    arch = "64" if sys.maxsize > 2**32 else "32"
    basic_arch_strings = {
        "32": "386",
        "64": "amd64"
    }

    for name, binary_data in binary_params.items():
        try:
            success = install_binary(binary_dir = binary_dir,
                                     download_log = download_log,
                                     name = name,
                                     source_url_format = binary_data["source_url_format"],
                                     file_name_format = binary_data["file_name_format"],
                                     checksum_file_name_format = binary_data.get("checksum_file_name_format"),
                                     checksum_algorithm = binary_data.get("checksum_algorithm"),
                                     release_version = binary_data.get("release_version"),
                                     use_gzip = binary_data.get("compressed", False),
                                     arch = arch,
                                     arch_strings = binary_data.get("arch_strings", basic_arch_strings))
        except KeyError as e:
            logging.error(f"Missing required binary download parameter for {name}: {e}")
            success = False
        except requests.RequestException as e:
            logging.error(f"Encountered an error during an HTTP request: {e}")
            success = False

        if (not success) and (not ignore_errors):
            return 1

    return 0


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
