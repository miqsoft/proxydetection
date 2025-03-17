#!/bin/bash
# use easy-rsa to generate keys for OpenVPN non interactively (DO NOT USE IN PRODUCTION)
# make sure to have easy-rsa installed and potentially change the path to easy-rsa

# Set the server's common name
SERVER_CN="server"

cd cert/
ln -s /usr/share/easy-rsa/easyrsa .

export EASYRSA_ALGO=ec
export EASYRSA_DIGEST=sha512
export EASYRSA_BATCH=1
export EASYRSA_REQ_CN="$SERVER_CN"
export EASYRSA_REQ_COUNTRY="US"
export EASYRSA_REQ_PROVINCE="New York"
export EASYRSA_REQ_CITY="New York"
export EASYRSA_REQ_ORG="My Organization"
export EASYRSA_REQ_EMAIL="[email protected]"
export EASYRSA_REQ_OU="IT Department"

# Initialize the PKI (Public Key Infrastructure)
./easyrsa init-pki

# Build the Certificate Authority (CA) without a passphrase
./easyrsa build-ca nopass

# Generate the server certificate and key
./easyrsa gen-req "$SERVER_CN" nopass
./easyrsa sign-req server "$SERVER_CN"

# Generate Diffie-Hellman parameters
./easyrsa gen-dh

# Generate a client certificate and key
./easyrsa gen-req client nopass
# Sign the client certificate with the CA
./easyrsa sign-req client client



