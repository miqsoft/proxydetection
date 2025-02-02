#!/bin/bash

echo "start apt update"
apt-get update > /dev/null
echo "end apt update"
apt-get install -y python3 python3-pip

cp /app/http1.service /etc/systemd/system/http1.service
systemctl daemon-reload
systemctl enable http1.service
systemctl start http1.service