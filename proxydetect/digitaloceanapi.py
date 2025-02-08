import os
from contextlib import contextmanager
import time
import pydo
from pssh.clients import SSHClient
import azure.core.exceptions
from proxydetect.machine import Machine
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()
DIGITAL_OCEAN_TOKEN = os.getenv('DIGITAL_OCEAN_TOKEN')
CLIENT = pydo.Client(DIGITAL_OCEAN_TOKEN)
PKEY=os.getenv('SSH_PKEY')

import logging
log = logging.getLogger(__name__)

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



# @contextmanager
# def create_droplet(droplet_config: dict):
#     ip_addr = droplet_config['ip']
#     del droplet_config['ip']
#     droplet = Droplet(**droplet_config)
#     droplet.create()
#     print("Droplet created, waiting for it to be online...")
#
#     try:
#         seconds_waited = 0
#         while seconds_waited < 120:
#             if droplet.status() == 'active':
#                 print("\nDroplet is online.")
#                 droplet.assign_reserved_ip(ip_addr)
#                 print(f"Assigned IP {ip_addr} to droplet.")
#                 break
#
#             print(f"\rWaited seconds: {seconds_waited}", end="")
#             time.sleep(1)
#             seconds_waited += 1
#
#         if droplet.status() != 'active':
#             raise DigitalOceanException("Droplet did not become active in time.")
#
#         yield droplet
#     finally:
#         droplet.destroy()
#         print("\nDroplet destroyed.")
#
#
# @contextmanager
# def create_droplets(droplet_configs: dict):
#     droplets = {}
#     for name, config in droplet_configs.items():
#         config_without_ip = config.copy()
#         del config_without_ip['ip']
#         droplet = Droplet(**config_without_ip)
#         droplets[name] = droplet
#         droplet.create()
#         print(f"Droplet {name} created, waiting for it to be online...")
#
#     try:
#         seconds_waited = 0
#         all_active = False
#         while seconds_waited < 120:
#             all_active = all(
#                 droplet.status() == 'active'
#                 for name, droplet in droplets.items()
#             )
#             if all_active:
#                 print("\nAll droplets are online.")
#                 break
#
#             print(f"\rWaited seconds: {seconds_waited}", end="")
#             time.sleep(1)
#             seconds_waited += 1
#
#         for name, droplet in droplets.items():
#             ip_addr = droplet_configs[name]['ip']
#             droplet.assign_reserved_ip(ip_addr)
#             print(f"Assigned IP {ip_addr} to droplet {name}.")
#
#         if not all_active:
#             raise DigitalOceanException("Not all droplets became active in time.")
#         yield droplets
#
#     finally:
#         for name, droplet in droplets.items():
#             try:
#                 droplet.destroy()
#                 print(f"Droplet {name} destroyed.")
#             except DigitalOceanException as e:
#                 print(f"Failed to destroy droplet {name}: {e}")
#                 continue


class DigitalOceanMachine(Machine):
    name: str
    id: int
    ip: str or None
    reserved_ip: str or None
    region: str
    ram: int
    cpu: int

    def __init__(self, config: dict, name: str,reserved_ip: str = None, ip: str = None, domain: str = None, output_dir: Path = Path('/output'), app_dir: Path = Path('/app')):
        super().__init__(name, ip, domain, output_dir, app_dir)
        # check if ram, cpu, region are in config (if not raise error)
        self.id = -1
        self.reserved_ip = reserved_ip
        try:
            self.ram = config['ram']
            self.cpu = config['cpu']
            self.region = config['region']
        except KeyError as e:
            raise ValueError("config must contain keys 'ram', 'cpu', 'region'") from e

        self.id = self.__get_id_by_name()


    def start(self):
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
        if 'droplet' not in resp:
            raise DigitalOceanException("Failed to create droplet.")
        self.id = resp['droplet']['id']
        if self.reserved_ip is not None:
            self.assign_reserved_ip(self.reserved_ip)

    def __get_id_by_name(self):
        droplets = CLIENT.droplets.list()
        return next(
            (
                droplet['id']
                for droplet in droplets['droplets']
                if droplet['name'] == self.name
            ),
            -1,
        )

    def status(self):
        if self.id == -1:
            self.id = self.__get_id_by_name()
        if self.id == -1:
            return 'not found'
        resp = CLIENT.droplets.get(self.id)
        return resp['droplet']['status']

    def is_online(self):
        return self.status() == 'active'

    def assign_reserved_ip(self, ip: str):
        req = {
            "droplet_id": self.id,
            "type": "assign"
        }
        # used to avoid azure.core.exceptions.HttpResponseError: (None) Droplet already has a pending event.
        resp = None
        for _ in range(10):
            try:
                resp = CLIENT.reserved_ips_actions.post(reserved_ip=ip, body=req)
                break
            except azure.core.exceptions.HttpResponseError as e:
                if "pending event" in str(e):
                    time.sleep(6)
                else:
                    raise e
        if not resp or 'action' not in resp:
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
        self.id = -1

    def stop(self):
        self.destroy()

    def ssh(self, command: str):
        client = SSHClient(self.domain, user='root', pkey=PKEY)
        host_output = client.run_command(command)
        print(f"{self.domain}: {command}")
        for line in host_output.stdout:
            print(f'\t {line}')
        for line in host_output.stderr:
            print(f'\tX {line}')


    def scp_copy_file(self, source: str, dest: str, direction: str = 'to'):
        if direction not in ['to', 'from']:
            raise ValueError("direction must be 'to' or 'from'")
        client = SSHClient(self.domain, user='root', pkey=PKEY)
        if direction == 'to':
            client.copy_file(source, dest)
        else:
            client.copy_remote_file(source, dest)

    def scp_copy_dir(self, source: str, dest: str, direction: str = 'to'):
        if direction not in ['to', 'from']:
            raise ValueError("direction must be 'to' or 'from'")
        client = SSHClient(self.domain, user='root', pkey=PKEY)
        if direction == 'to':
            client.copy_file(source, dest, recurse=True)
        else:
            client.copy_remote_file(source, dest, recurse=True)

    def start_pcap(self, interface: str, outputfile: str, log: str = '/dev/null'):
        self.ssh(f"nohup sudo tcpdump -i {interface} -w {outputfile} > {log} 2>&1 & disown")

    def stop_pcap(self):
        self.ssh("killall tcpdump")



        
    