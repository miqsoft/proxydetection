#!/bin/bash
set -o nounset -o pipefail -o errexit

# Load all variables from .env and export them all for Ansible to read
set -o allexport
source "$(dirname "$0")/.env"
set +o allexport

ansible-playbook stop.yml -e "target=client"
ansible-playbook stop.yml -e "target=relay"
ansible-playbook stop.yml -e "target=server"
