#!/bin/bash

mkdir -p cert
cd cert

# generate ssh key pair
ssh-keygen -t rsa -b 4096 -f id_rsa -N ""
