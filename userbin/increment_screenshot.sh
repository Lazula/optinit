#!/bin/bash

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <screenshot>"
  exit
fi

screenshot_file="$1"

screenshot_id=$(echo "$screenshot_file" | cut -d"_" -f1)
new_id=$(( $screenshot_id + 1 ))

new_file=$(echo "$screenshot_file" | sed "s/$screenshot_id/$new_id/")

mv -v -i "$screenshot_file" "$new_file"
