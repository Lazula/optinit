#!/bin/bash

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
