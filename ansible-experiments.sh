#!/bin/bash
set -o nounset -o pipefail -o errexit

# Load all variables from .env and export them all for Ansible to read
set -o allexport
source "$(dirname "$0")/.env"
set +o allexport

# Get first argument (directory)
directory=$1

# Get second argument (subset), optional
subset="${2:-}"  # Defaults to empty if not set

# Loop through all files in the directory
for file in "$directory"/*; do
  echo "Processing $file"
  # Check if the file is a regular file
  if [ -f "$file" ]; then
    # Skip files where name starts with x_
    basename=$(basename "$file")
    if [[ $basename == x_* ]]; then
      echo "Skipping $file"
      continue
    fi
    # skip file that are not yml
    if [[ $basename != *.yml ]]; then
      echo "Skipping $file"
      continue
    fi
    # If subset is set and does not match basename, skip
    if [[ -n $subset && $basename != ${subset}_* ]]; then
      echo "Skipping $file (does not match subset '$subset')"
      continue
    fi
    # Run ansible-playbook
    ansible-playbook experiment.yml -e "experiment_file=$file"
  fi
done
