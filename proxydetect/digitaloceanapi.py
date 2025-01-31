import os
from contextlib import contextmanager
import time
import pydo

from dotenv import load_dotenv
load_dotenv()
DIGITAL_OCEAN_TOKEN = os.getenv('DIGITAL_OCEAN_TOKEN')
CLIENT = pydo.Client(DIGITAL_OCEAN_TOKEN)

class DigitalOceanException(Exception):
    pass

def _wait_for_action(action_id: int, wait_seconds: int = 3, timeout_seconds: int = 120):
    resp = CLIENT.actions.get(action_id)
    status = resp["action"]["status"]
    total_waited = 0

    while status == "in-progress" and total_waited < timeout_seconds:
        resp = CLIENT.actions.get(action_id)
        status = resp["action"]["status"]
        if status == "in-progress":
            time.sleep(wait_seconds)
            total_waited += wait_seconds
        elif status == "errored":
            raise DigitalOceanException("Action errored.")

    if status != "completed":
        raise DigitalOceanException("Action did not complete in time.")

class Droplet:
    name: str
    id: int
    ip: str or None
    reserved_ip: str or None
    region: str
    ram: int
    cpu: int

    def __init__(self, name: str, ram: int = 4, cpu: int = 2, region: str = 'fra1'):
        self.name = name
        self.ram = ram
        self.cpu = cpu
        self.region = region
        self.reserved_ip = None
        self.ip = None

    def create(self):
        keys = CLIENT.ssh_keys.list()["ssh_keys"]
        droplet = {
            "name": self.name,
            "region": self.region,
            "image": "ubuntu-24-04-x64",
            "size": f"s-{self.cpu}vcpu-{self.ram}gb",
            "backups": False,
            "ssh_keys": [key['id'] for key in keys],
        }
        resp = CLIENT.droplets.create(body=droplet)
        if not 'droplet' in resp:
            raise DigitalOceanException("Failed to create droplet.")
        self.id = resp['droplet']['id']

    def status(self):
        resp = CLIENT.droplets.get(self.id)
        return resp['droplet']['status']

    def assign_reserved_ip(self, ip: str):
        req = {
            "droplet_id": self.id,
            "type": "assign"
        }
        resp = CLIENT.reserved_ips_actions.post(reserved_ip=ip, body=req)
        if not 'action' in resp:
            raise DigitalOceanException("Failed to assign IP to droplet.")
        action_id = resp['action']['id']
        _wait_for_action(action_id)
        self.reserved_ip = ip

    def destroy(self):
        resp = CLIENT.droplets.destroy(droplet_id=self.id)
        if resp is not None:
            raise DigitalOceanException(f"Failed to destroy droplet {self.id}. ({resp})")
        self.ip = None
        self.reserved_ip = None



@contextmanager
def create_droplet(droplet_config):
    ip_addr = droplet_config['ip']
    del droplet_config['ip']
    droplet = Droplet(**droplet_config)
    droplet.create()
    print("Droplet created, waiting for it to be online...")

    try:
        seconds_waited = 0
        while seconds_waited < 120:
            if droplet.status() == 'active':
                print("\nDroplet is online.")
                droplet.assign_reserved_ip(ip_addr)
                print(f"Assigned IP {ip_addr} to droplet.")
                break

            print(f"\rWaited seconds: {seconds_waited}", end="")
            time.sleep(1)
            seconds_waited += 1

        if droplet.status() != 'active':
            raise DigitalOceanException("Droplet did not become active in time.")

        yield droplet
    finally:
        droplet.destroy()
        print("\nDroplet destroyed.")