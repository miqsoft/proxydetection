from pathlib import Path
import os

from dotenv import load_dotenv
load_dotenv()


RESERVED_IP = {
    'relay': '104.248.101.195',
    'server': '68.183.243.119'
}

DNS = {
    'relay': 'proxy.labforensic.de',
    'server': 'server.labforensic.de'
}

SERVER_DROPLET = {
    'name': 'server',
    'ip': RESERVED_IP['server'],
    'ram': 4,
    'cpu': 2,
    'region': 'fra1',
}

RELAY_DROPLET = {
    'name': 'relay',
    'ip': RESERVED_IP['relay'],
    'ram': 4,
    'cpu': 2,
    'region': 'fra1',
}


BASE_DIR = Path(os.getenv('BASE_DIR'))
RUN_DIR = BASE_DIR / 'run'
CERT_DIR = BASE_DIR / 'cert'
SETUP_DIR = BASE_DIR / 'setups'
DATA_DIR = BASE_DIR / 'data'
