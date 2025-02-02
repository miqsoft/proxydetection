#!/bin/bash

# create a new user proxy (with home directory /home/proxy)
useradd -m proxy
# change the password of the user proxy to proxy
echo "proxy:proxy" | chpasswd
# change the shell of the user proxy to /bin/bash
chsh -s /bin/bash proxy


# Installation
apt-get update
apt install gcc make git -y
cd /home/
git clone https://github.com/z3apa3a/3proxy
cd 3proxy
make -f Makefile.Linux
make -f Makefile.Linux install
## exchange chroot /usr/local/3proxy proxy proxy by chroot /usr/local/3proxy root root in "/etc/3proxy/3proxy.cfg"
#sed -i 's|chroot /usr/local/3proxy proxy proxy|chroot /usr/local/3proxy root root|g' /etc/3proxy/3proxy.cfg
## change owner of 3proxy to avoid permission issues
sudo chown -R proxy:proxy /usr/local/3proxy
# add a user
chmod +x /usr/local/3proxy/conf/add3proxyuser.sh
/usr/local/3proxy/conf/add3proxyuser.sh proxy proxy
# exchange "auth strong" by "auth none" in "/etc/3proxy/3proxy.cfg"
sed -i 's/auth strong/auth none/g' /usr/local/3proxy/conf/3proxy.cfg


update-rc.d 3proxy defaults

# start 3proxy
service 3proxy start
