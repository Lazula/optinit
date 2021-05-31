#!/bin/bash
#
# SPDX-FileCopyrightText: (C) 2021 Lazula <26179473+Lazula@users.noreply.github.com>
# SPDX-License-Identifier: GPL-3.0-or-later

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <target name> <target ip> [nmap options...]"
  exit
fi

name="$1"
ip="$2"
shift 2

mkdir -p nmap

if [ "$EUID" -eq 0 ]; then
  scan_type="-sS"
else
  scan_type="-sC"
fi

# Full port service scan
nmap $ip $scan_type -p- -T 4 -sV -oA nmap/all_ports $@
# Extract list of open ports
ports=$(grep -oE '[0-9]+/open' nmap/all_ports.gnmap | grep -oE '[0-9]+' | tr '\n' ',' | rev | cut -b2- | rev)
echo "$ports" | tr ',' '\n' > nmap/open_ports.lst
# Service scan, OS detection
nmap $ip $scan_type -p $ports -A -oA nmap/$name $@ && cp nmap/$name.nmap $name.txt
