from proxydetect.digitaloceanapi import create_droplet, create_droplets
import paramiko

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


def create_ssh_client(ip, username='root', key_filename='~/.ssh/id_ecdsa'):
    client = paramiko.SSHClient()
    key = paramiko.ECDSAKey.from_private_key_file(key_filename)
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    client.connect(ip, username=username, pkey=key)
    return client


if __name__ == '__main__':
    droplets = {
        'server': SERVER_DROPLET,
        'proxy': PROXY_DROPLET,
    }

    with create_droplets(droplets) as droplets:
        ssh_proxy = create_ssh_client(RESERVED_IP['proxy'])
        ssh_server = create_ssh_client(RESERVED_IP['server'])

        input("Press Enter to destroy droplets...")



