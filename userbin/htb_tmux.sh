#!/bin/bash
#
# SPDX-FileCopyrightText: (C) 2021 Lazula <26179473+Lazula@users.noreply.github.com>
# SPDX-License-Identifier: GPL-3.0-or-later

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 machine-name"
  exit 1
fi

NAME="$1"

mkdir -p ~/htb/${NAME}/screenshots
mkdir -p ~/htb/${NAME}/nmap
touch ~/htb/${NAME}/nmap/${NAME}.nmap
touch ~/htb/${NAME}/${NAME}.txt

cd ~/htb/${NAME}

tmux new-session \;                               \
rename-window "http_serv" \;                      \
send-keys "serv-http" C-m \; \
new-window \;                                     \
rename-window "$NAME" \;                          \
split-window -v \;                                \
select-pane -U

cd - >/dev/null
