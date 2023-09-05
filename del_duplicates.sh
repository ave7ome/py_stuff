#!/bin/bash

declare -A arr
shopt -s globstar

i=0

for file in DIRECTORY/configurations/**/*; do
  [[ -f "$file" ]] || continue

  read cksm _ < <(md5sum "$file")
  if ((arr[$cksm]++)); then
    echo "rm $file"
    rm $file
    i=i+1
  fi
done

echo "______________________________________"
echo "$i files deleted"
echo "Cleanup completed"
