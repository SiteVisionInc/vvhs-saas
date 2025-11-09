#!/bin/bash

# Define output file
OUTPUT="code-files-list.txt"

# Define file patterns to match
MATCHES=(
  "*.py"
  "*.ts"
  "*.sql"
  "*.tsx"
  "*.css"
  "Dockerfile"
  ".env"
  "docker-compose.yml"
)

# Clear output file
> "$OUTPUT"

echo "Writing matching files and contents to $OUTPUT..."

# Directories to search
SEARCH_DIRS=(./frontend/src ./api)

# Loop through each pattern and directory
for dir in "${SEARCH_DIRS[@]}"; do
  for pattern in "${MATCHES[@]}"; do
    find "$dir" -type f -name "$pattern" ! -path "*/__pycache__/*" | while read -r file; do
      {
        echo "======================================"
        echo "File: $(basename "$file")"
        echo "Path: $(dirname "$file")"
        echo "--------------------------------------"
        cat "$file"
        echo "======================================"
        echo ""
      } >> "$OUTPUT"
    done
  done
done

# Explicitly include ./docker-compose.yml if it exists
if [ -f "./docker-compose.yml" ]; then
  {
    echo "======================================"
    echo "File: docker-compose.yml"
    echo "Path: ."
    echo "--------------------------------------"
    cat "./docker-compose.yml"
    echo "======================================"
    echo ""
  } >> "$OUTPUT"
fi
