#!/bin/bash

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <sequence start> <sequence end>"
  exit
fi

# Confirm that one entry exists for each number
for i in $(seq $1 $2); do
  num_entries=$(ls -1 ${i}_* | wc -l)
  if [ "$num_entries" -ne 1 ]; then
    echo "Multiple entries:"
    ls -1 ${i}_*
    echo "Cannot continue."
    exit
  fi
done

# Work in reverse to avoid overwrites
for i in $(seq $2 -1 $1); do
  entry=$(ls ${i}_*)
  $(dirname $0)/increment_screenshot.sh $entry
done
