import time
from proxydetect.digitaloceanapi import create_droplet, create_droplets
from vagrantapi import VagrantBox, render_vagrantfile
from pathlib import Path
import os

from dotenv import load_dotenv
load_dotenv()

RESERVED_IP = {
    'proxy': '104.248.101.195',
    'server': '68.183.243.119'
}

DNS = {
    'proxy': 'proxy.labforensic.de',
    'server': 'server.labforensic.de'
}

SERVER_DROPLET = {
    'name': 'server',
    'ip': RESERVED_IP['server'],
    'ram': 4,
    'cpu': 2,
    'region': 'fra1',
}

PROXY_DROPLET = {
    'name': 'proxy',
    'ip': RESERVED_IP['proxy'],
    'ram': 4,
    'cpu': 2,
    'region': 'fra1',
}

CLIENT_VAGRANTDIR_MAP = {
    'default': 'client/default/Vagrantfile',
}


if __name__ == '__main__':
    droplets = {
        'server': SERVER_DROPLET,
        'proxy': PROXY_DROPLET,
    }
    PROXY_DNS = DNS['proxy']
    SERVER_DNS = DNS['server']
    PROXY_IP = RESERVED_IP['proxy']
    SERVER_IP = RESERVED_IP['server']
    BASE_DIR = Path(os.getenv('BASE_DIR'))
    RESULT_DIR = BASE_DIR/'pcaps'
    RUN_DIR = BASE_DIR/'run'
    RELAY_APP_DIR = BASE_DIR/'relay'/'3proxy'
    SERVER_APP_DIR = BASE_DIR/'server'/'default'
    render_vagrantfile(BASE_DIR/CLIENT_VAGRANTDIR_MAP['default'], RUN_DIR/'Vagrantfile', RESULT_DIR, BASE_DIR)


    with VagrantBox(RUN_DIR) as client:
        with create_droplet(SERVER_DROPLET) as server:
            with create_droplet(PROXY_DROPLET) as proxy:
                proxy.ssh('mkdir -p /app')
                proxy.ssh('mkdir -p /output')
                proxy.scp_copy_dir(RELAY_APP_DIR, '/app', direction='to')

                server.ssh('mkdir -p /app')
                server.ssh('mkdir -p /output')
                server.scp_copy_dir(SERVER_APP_DIR, '/app', direction='to')

                # remove crlf from scripts (for windows)
                proxy.ssh(r"sed -i 's/\r$//' /app/setup.sh")
                proxy.ssh("chmod +x /app/setup.sh && /app/setup.sh")
                server.ssh(r"sed -i 's/\r$//' /app/setup.sh")
                server.ssh('chmod +x /app/setup.sh && /app/setup.sh')

                client.start_pcap('eth0', '/vagrant/results/client.pcap', log='/vagrant/results/tcpdump_client.log')
                print('client: capture started')
                proxy.start_pcap('eth0', '/output/proxy.pcap', log='/output/tcpdump_proxy.log')
                print('proxy: capture started')
                server.start_pcap('eth0', '/output/server.pcap', log='/output/tcpdump_server.log')
                print('server: capture started')

                print(f'client: run - export http_proxy=http://{PROXY_IP}:3128 && curl -v http://{SERVER_IP}')
                client.ssh(f'export http_proxy=http://{PROXY_IP}:3128 && curl -v http://{SERVER_IP}')
                print('client: request sent')

                client.stop_pcap()
                print('client: capture stopped')
                proxy.stop_pcap()
                print('proxy: capture stopped')
                server.stop_pcap()
                print('server: capture stopped')

                proxy.scp_copy_file('/output/proxy.pcap', (RESULT_DIR/'proxy.pcap').as_posix(), direction='from')
                server.scp_copy_file('/output/server.pcap', (RESULT_DIR/'server.pcap').as_posix(), direction='from')




