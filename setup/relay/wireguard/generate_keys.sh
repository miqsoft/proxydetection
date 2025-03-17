#!/bin/bash
# use wireguard (wg) to generate keys for Wireguard non interactively (DO NOT USE IN PRODUCTION)

mkdir -p cert
cd cert/

# Generate private key
wg genkey > ./private_server

# Generate public key
cat private_server | wg pubkey > ./public_server

# Generate private key (client)
wg genkey > ./private_client

# Generate public key (client)
cat private_client | wg pubkey > ./public_client






