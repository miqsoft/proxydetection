#!/bin/bash

rm -rf ./ca
make-cadir ./ca
cd ca

./easyrsa init-pki

export EASYRSA_BATCH=1
./easyrsa build-ca nopass

./easyrsa build-server-full ForensicVPNServer1 nopass
./easyrsa build-client-full ForensicVPNClient1 nopass

./easyrsa gen-dh

cd ..
cp ./ca/pki/dh.pem ./dh.pem
cp ./ca/pki/ca.crt ./ca.crt
cp ./ca/pki/issued/ForensicVPNServer1.crt ./server.crt
cp ./ca/pki/private/ForensicVPNServer1.key ./server.key
cp ./ca/pki/issued/ForensicVPNClient1.crt ./client.crt
cp ./ca/pki/private/ForensicVPNClient1.key ./client.key