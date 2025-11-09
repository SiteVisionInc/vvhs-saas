#!/bin/bash

# Output file
OUTPUT="directory_structure.txt"

# Root label
ROOT_LABEL="-$(basename "$PWD")/"

# Write root label
echo "$ROOT_LABEL" > "$OUTPUT"

# Generate tree-like structure
find . | awk '
BEGIN {FS="/"}
{
  indent = ""
  for (i = 2; i < NF; i++) indent = indent "│   "
  if (NF > 1) {
    if ($0 ~ /\/$/) {
      print indent "├── " $NF "/"
    } else {
      print indent "├── " $NF
    }
  } else {
    print $0
  }
}' >> "$OUTPUT"

