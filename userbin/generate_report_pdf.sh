#!/bin/bash
#
# SPDX-FileCopyrightText: (C) 2021 Lazula <26179473+Lazula@users.noreply.github.com>
# SPDX-License-Identifier: GPL-3.0-or-later

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <report (md)> <output file (pdf)> [-q]"
  echo "-q disables automatically opening the output."
  exit 1
fi

report=$1
output=$2
quiet=$3

# Added "listings" to highlight code blocks.

pandoc ${report} \
-o ${output} \
--from markdown+yaml_metadata_block+raw_html \
--template eisvogel \
--table-of-contents \
--toc-depth 6 \
--number-sections \
--top-level-division=chapter \
--highlight-style=espresso \
--listings

if [ "$quiet" != "-q" ]; then
  xdg-open ${output}
fi
