#!/bin/bash

if [ "$#" != 2 ]; then
  echo "Usage: $0 <linpeas output file>"
  exit 1
fi

linpeas_output_file="$1"

C=$'\033'
NC="${C}[0m"
RED_YELLOW="${C}[1;31;103m"
RED="${C}[1;31m"

LEVEL_VERY_HIGH_GREP="${C}\[1;31;103m"
LEVEL_HIGH_GREP="${C}\[1;31m"

echo "${RED_YELLOW}Very high risk${NC}:"
grep "${LEVEL_VERY_HIGH_GREP}" ${linpeas_output_file} | tail -n +2

echo
echo
echo "${RED}High risk${NC}:"
grep "${LEVEL_HIGH_GREP}" ${linpeas_output_file} | tail -n +2
