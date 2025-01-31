from proxydetect.digitaloceanapi import create_droplet

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
    'name': 'server',
    'ip': RESERVED_IP['server'],
    'ram': 4,
    'cpu': 2,
    'region': 'fra1',
}

if __name__ == '__main__':
    droplets = {
        'server': SERVER_DROPLET,
        # 'proxy': PROXY_DROPLET,
    }

    with create_droplet(SERVER_DROPLET) as server:
        input("Press Enter to destroy droplets...")



