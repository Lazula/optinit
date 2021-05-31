#!/bin/bash
#
# SPDX-FileCopyrightText: (C) 2021 Lazula <26179473+Lazula@users.noreply.github.com>
# SPDX-License-Identifier: GPL-3.0-or-later

DEBUG=0

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <LHOST> <LPORT>"
  exit 1
fi

NEW_LHOST="$1"
NEW_LPORT="$2"

ORIGINAL_BASE_PATH=$(dirname $0)/../shell/original
NEW_BASE_PATH=$(dirname $0)/../shell

dirs=$(find ${ORIGINAL_BASE_PATH} -type d)
for dir in $dirs; do
  if [ -n "$(echo "$dir" | grep '\.git')" ]; then continue; fi
  if [ $DEBUG -gt 0 ]; then echo "dir=$dir"; fi
  new_dir=$(echo -n "$dir" | sed -e "s|${ORIGINAL_BASE_PATH}|${NEW_BASE_PATH}|")
  if [ $DEBUG -gt 0 ]; then echo "new_dir=$new_dir"; echo; fi
  mkdir -p "$new_dir" 2>/dev/null
done

files=$(find ${ORIGINAL_BASE_PATH} -type f)
for file in $files; do
  if [ $DEBUG -gt 0 ]; then echo "file=$file"; fi
  new_file=$(echo -n "$file" | sed -e "s|${ORIGINAL_BASE_PATH}|${NEW_BASE_PATH}|")
  if grep -q "REPLACEME" "$file"; then
    if [ $DEBUG -gt 0 ]; then echo "new_file=$new_file"; echo; fi
    cp "$file" "$new_file" 2>/dev/null
    sed -e "s/REPLACEME_LHOST/${NEW_LHOST}/g" \
        -e "s/REPLACEME_LPORT/${NEW_LPORT}/g" -i "$new_file" 2>/dev/null
  else
    if [ $DEBUG -gt 0 ]; then echo "$file is not a shell. skipping."; fi
    continue
  fi
done
