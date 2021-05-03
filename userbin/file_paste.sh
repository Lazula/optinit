#!/bin/bash

if [ "$#" != 2 ]; then
  echo "Usage: $0 <file> <name>"
  exit 1
fi

file="$1"
name="$2"

if ! test -e "$file"; then
  echo "$file does not exist."
  exit 1
fi

is_first_line=1
while IFS= read -r line; do
  if test $is_first_line -eq 1; then
    echo "echo '$(sed "s/'/'\\\''/g" <<< "$line")' > $name"
    is_first_line=0
  else
    echo "echo '$(sed "s/'/'\\\''/g" <<< "$line")' >> $name"
  fi
done < $file
