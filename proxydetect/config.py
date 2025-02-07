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

