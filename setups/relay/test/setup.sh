#!/bin/bash

apt-get update && apt upgrade -y
apt-get install -y python3 python3-pip python3.12-venv
apt install -y python3.12-venv
python3 -m venv /root/venv
source /root/venv/bin/activate
pip3 install -r /app/requirements.txt


