#!/bin/bash
#
# SPDX-FileCopyrightText: (C) 2021 Lazula <26179473+Lazula@users.noreply.github.com>
# SPDX-License-Identifier: GPL-3.0-or-later

if [ "$#" -lt 2 ]; then
  echo "Compare two different folders and show files"
  echo "that differ between the two. Intended for use"
  echo "with two near-identical folders."
  echo "Usage: $0 <folder 1> <folder 2> [max depth]"
  exit 1
fi

FOLDER_1="$(readlink -en "$1")"
FOLDER_2="$(readlink -en "$2")"

if [ -n "$3" ]; then
  DEPTH="-maxdepth $3"
else
  DEPTH=""
fi

TMPDIR=$(mktemp -d)

cd "$TMPDIR"
ln -s "$FOLDER_1" 1
ln -s "$FOLDER_2" 2
find 1/ 2/ $DEPTH -type f -exec md5sum {} \; | \
  sed 's/  [12]\//  /g' > hashes
echo "The following files differ between the two folders:"
sort hashes | uniq -c | sort -nr | grep '^      1' | \
  awk 'NR % 2 {print}' | cut -d' ' -f10-
cd - >/dev/null
rm -rf "$TMPDIR"
