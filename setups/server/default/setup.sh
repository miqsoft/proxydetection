#!/bin/bash

apt-get update && apt upgrade -y
apt-get install -y python3 python3-pip python3.12-venv
apt install -y python3.12-venv
python3 -m venv /root/venv
source /root/venv/bin/activate
pip3 install -r /app/requirements.txt

# install caddy
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install -y caddy
pkill -9 caddy

# install unbound
apt-get install bind9-utils dnsutils net-tools -y
apt-get install -y unbound

touch /output/server_dns.log
chown unbound:unbound /output/server_dns.log
cp /app/unbound.conf /etc/unbound/unbound.conf.d/myunbound.conf

# install vsftpd
apt install -y vsftpd
cp /app/vsftpd.conf /etc/vsftpd.conf
cp /app/vsftpd2.conf /etc/vsftpd2.conf

#
mkdir -p ~/.ssh2/
touch ~/.ssh2/authorized_keys
chmod -R 700 ~/.ssh2/

# setup ftp
FTP_USER="ftpuser"
FTP_PASS="ultra!secret!password"
FTP_DIR="/home/$FTP_USER/ftp"
TEST_FILE="$FTP_DIR/test.txt"
# Create FTP user and set password
sudo useradd -m -d $FTP_DIR -s /bin/bash $FTP_USER
echo "$FTP_USER:$FTP_PASS" | sudo chpasswd
echo "$FTP_USER" > /etc/vsftpd.userlist

# Set correct permissions
sudo chmod a-w $FTP_DIR
sudo mkdir -p "$FTP_DIR/files"
sudo chown $FTP_USER:$FTP_USER "$FTP_DIR/files"

# Create test file
echo "Hello FTP" | sudo tee "$TEST_FILE" > /dev/null
sudo chmod 644 "$TEST_FILE"


cp /app/http1.service /etc/systemd/system/http1.service
cp /app/http2.service /etc/systemd/system/http2.service
cp /app/ws.service /etc/systemd/system/ws.service
cp /app/wss.service /etc/systemd/system/wss.service
cp /app/https1.service /etc/systemd/system/https1.service
cp /app/https2.service /etc/systemd/system/https2.service
cp /app/https3.service /etc/systemd/system/https3.service
cp /cert/id_rsa.pub /etc/ssh/id_rsa.pub
cp /app/sshd_config2 /etc/ssh/sshd_config2
cp /app/sshd2.service /etc/systemd/system/ssh2.service
cp /app/vsftpd2.service /etc/systemd/system/vsftpd2.service

systemctl daemon-reload
systemctl enable http1.service
systemctl enable http2.service
systemctl enable ws.service
systemctl enable wss.service
systemctl enable https1.service
systemctl enable https2.service
systemctl enable https3.service
systemctl enable ssh2.service
systemctl enable unbound
systemctl enable vsftpd
systemctl enable vsftpd2

systemctl start http1.service
systemctl start http2.service
systemctl start ws.service
systemctl start wss.service
systemctl start https1.service
systemctl start https2.service
systemctl start https3.service
systemctl start ssh2.service
systemctl start unbound
systemctl start vsftpd
systemctl start vsftpd2