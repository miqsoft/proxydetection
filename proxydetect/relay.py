from proxydetect.config import RESERVED_IP, DNS, RELAY_DROPLET, BASE_DIR, CERT_DIR, SETUP_DIR
from proxydetect.digitaloceanapi import DigitalOceanMachine

import logging
log = logging.getLogger(__name__)

NAME = 'relay'
RESERVED_IP = RESERVED_IP['relay']
DNS = DNS['relay']
CONFIG = RELAY_DROPLET


def __setup_relay(machine: DigitalOceanMachine, setup: str):
    machine.ssh('mkdir -p /app')
    machine.ssh('mkdir -p /cert')
    machine.ssh('mkdir -p /output')
    relay_app_dir = SETUP_DIR / 'relay' / setup
    machine.scp_copy_dir(relay_app_dir, '/app', direction='to')
    machine.scp_copy_dir(CERT_DIR, '/cert', direction='to')

    machine.ssh(r"sed -i 's/\r$//' /app/setup.sh")
    machine.ssh('chmod +x /app/setup.sh && /app/setup.sh')

def start_relay(args):
    log.info(f"Starting relay (with args: {args})")
    name = f'{NAME}-{args.setup}'
    machine = DigitalOceanMachine(config=CONFIG, name=name, domain=DNS, reserved_ip=RESERVED_IP)
    if machine.is_online():
        print("Server is already online")
    else:
        print("Start relay")
        machine.start()
        log.info("Server started")
    __setup_relay(machine, args.setup)
    print("Server setup completed")
    log.info("Server setup completed")


def stop_relay(args):
    log.info(f"Stopping relay (with args: {args})")
    name = f'{NAME}-{args.setup}'
    machine = DigitalOceanMachine(config=CONFIG, name=name, reserved_ip=RESERVED_IP, domain=DNS)
    machine.stop()
    log.info("Server stopped")


def destroy_relay(args):
    log.info(f"Destroying relay (with args: {args})")
    name = f'{NAME}-{args.setup}'
    machine = DigitalOceanMachine(config=CONFIG, name=name, reserved_ip=RESERVED_IP, domain=DNS)
    machine.destroy()
    log.info("Server destroyed")

def ssh_relay(args):
    log.info(f"Running SSH command on relay (with args: {args})")
    name = f'{NAME}-{args.setup}'
    machine = DigitalOceanMachine(config=CONFIG, name=name, reserved_ip=RESERVED_IP, domain=DNS)
    machine.ssh(args.cmd)
    log.info("SSH command run on relay")


def get_relay(setup):
    name = f'{NAME}-{setup}'
    return DigitalOceanMachine(config=CONFIG, name=name, reserved_ip=RESERVED_IP, domain=DNS)
