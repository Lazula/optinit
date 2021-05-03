#!/bin/bash

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 machine-name"
  exit 1
fi

NAME="$1"

mkdir -p ~/pg/${NAME}/screenshots
mkdir -p ~/pg/${NAME}/nmap
touch ~/pg/${NAME}/nmap/${NAME}.nmap
touch ~/pg/${NAME}/${NAME}.txt

cd ~/pg/${NAME}

tmux new-session \;                               \
rename-window "http_serv" \;                      \
send-keys "serv-http" C-m \; \
new-window \;                                     \
rename-window "$NAME" \;                          \
split-window -v \;                                \
select-pane -U

# Quietly switch back to old cwd once done
cd - >/dev/null
