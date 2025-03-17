#!/bin/bash
set -o nounset -o pipefail -o errexit

# Load all variables from .env and export them all for Ansible to read
set -o allexport
source "$(dirname "$0")/.env"
set +o allexport

ansible-playbook start.yml -e "target=client"
ansible-playbook start.yml -e "target=relay"
ansible-playbook setup.yml -e "target=client setup=setup/client/wireguard/default.yml"
ansible-playbook setup.yml -e "target=relay setup=setup/relay/wireguard/default.yml"
ansible-playbook start.yml -e "target=server"
ansible-playbook setup.yml -e "target=server setup=setup/server/default/default.yml"
