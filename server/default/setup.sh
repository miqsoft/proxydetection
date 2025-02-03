#!/bin/bash

echo "start apt update"
apt-get update > /dev/null
echo "end apt update"
apt-get install -y python3 python3-pip
pip3 install -r /app/requirements.txt

cp /app/http1.service /etc/systemd/system/http1.service
cp /app/http2.service /etc/systemd/system/http2.service
cp /app/http3.service /etc/systemd/system/http3.service
cp /app/websockets.service /etc/systemd/system/websockets.service
cp /app/https1.service /etc/systemd/system/https1.service
cp /app/https2.service /etc/systemd/system/https2.service
cp /app/https3.service /etc/systemd/system/https3.service

systemctl daemon-reload
systemctl enable http1.service
systemctl enable http2.service
systemctl enable http3.service
systemctl enable websockets.service
systemctl enable https1.service

systemctl start http1.service
systemctl start http2.service
systemctl start http3.service
systemctl start websockets.service
systemctl start https1.service