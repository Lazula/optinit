#!/bin/bash
#
# SPDX-FileCopyrightText: (C) 2021 Lazula <26179473+Lazula@users.noreply.github.com>
# SPDX-License-Identifier: GPL-3.0-or-later

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <screenshot> <id number>"
  exit
fi

screenshot_file="$1"
id="$2"

new_file="${id}_${screenshot_file}"

mv -v -i "$screenshot_file" "$new_file"
