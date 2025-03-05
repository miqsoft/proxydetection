#!/bin/bash
set -o nounset -o pipefail -o errexit

# Load all variables from .env and export them all for Ansible to read
set -o allexport
source "$(dirname "$0")/.env"
set +o allexport

# get first argument
directory=$1


# loop through all files in the directory
for file in $directory/*; do
  echo "Processing $file"
  # check if the file is file
  if [ -f "$file" ]; then
    ansible-playbook experiment.yml -e "experiment_file=$file"
  fi
done