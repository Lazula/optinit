#!/usr/bin/python3

import argparse
import socket

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate a set of commands that can be pasted into a noninteractive session to download files to the machine via FTP")
    parser.add_argument("lhost", type=str, help="The server IP to fetch files from")
    parser.add_argument("lport", type=int, help="The server port")
    parser.add_argument("target", type=str, choices=["L", "W"], help="The target operating system (Linux or Windows)")
    parser.add_argument("files", type=str, nargs="+", help="File names to download")
    parser.add_argument("-b", "--binary", action="store_true", help="Use binary mode")
    parser.add_argument("-p", "--passive", action="store_true", help="Use passive mode")

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


def print_commands(lhost, lport, target, files, binary=False, passive=False):
    ftp_commands = []
    ftp_commands.append(f"open {lhost} {lport}")
    ftp_commands.append("anonymous")
    ftp_commands.append("anonymous")

    if passive:
        ftp_commands.append("passive")
    if binary:
        ftp_commands.append("binary")

    for filename in files:
        ftp_commands.append(f"get {filename}")

    ftp_commands.append("quit")

    os_commands = []
    os_commands.append(f'echo "{ftp_commands[0]}" > ftp_dl.txt')
    for command in ftp_commands[1:]:
        os_commands.append(f'echo "{command}" >> ftp_dl.txt')

    if target == "L":
        os_commands.append("ftp < ftp_dl.txt")
    else:
        os_commands.append("ftp -s:ftp_dl.txt")

    if target == "L":
        os_commands.append("rm ftp_dl.txt")
    else:
        os_commands.append("del ftp_dl.txt")

    print(*os_commands, sep="\n")


def main():
    try:
        args = parse_arguments()
    except RuntimeError:
        print("An error was encountered during argument parsing.")
        exit(1)

    print_commands(args.lhost, args.lport, args.target, args.files, args.binary, args.passive)


if __name__ == "__main__":
    main()
