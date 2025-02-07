#!/bin/bash

apt-get update && apt upgrade -y
apt-get install -y python3 python3-pip python3.12-venv
# create venv
python3 -m venv /root/venv
source /root/venv/bin/activate
pip3 install -r /app/requirements.txt

cp /app/http1.service /etc/systemd/system/http1.service
cp /app/http2.service /etc/systemd/system/http2.service
cp /app/http3.service /etc/systemd/system/http3.service
cp /app/ws.service /etc/systemd/system/ws.service
cp /app/wss.service /etc/systemd/system/wss.service
cp /app/https1.service /etc/systemd/system/https1.service
cp /app/https2.service /etc/systemd/system/https2.service
cp /cert/id_rsa.pub /etc/ssh/id_rsa.pub
cp /app/sshd_config2 /etc/ssh/sshd_config2
cp /app/sshd2.service /etc/systemd/system/ssh2.service

systemctl daemon-reload
systemctl enable http1.service
systemctl enable http2.service
systemctl enable http3.service
systemctl enable ws.service
systemctl enable wss.service
systemctl enable https1.service
systemctl enable https2.service
systemctl enable ssh2.service

systemctl start http1.service
systemctl start http2.service
systemctl start http3.service
systemctl start ws.service
systemctl start wss.service
systemctl start https1.service
systemctl start https2.service
systemctl start ssh2.service