from proxydetect.config import RESERVED_IP, DNS, SERVER_DROPLET, BASE_DIR, CERT_DIR, SETUP_DIR
from proxydetect.digitaloceanapi import DigitalOceanMachine

import logging
log = logging.getLogger(__name__)

NAME = 'server'
RESERVED_IP = RESERVED_IP['server']
DNS = DNS['server']
CONFIG = SERVER_DROPLET


def __setup_server(machine: DigitalOceanMachine, setup: str):
    machine.ssh('mkdir -p /app')
    machine.ssh('mkdir -p /cert')
    machine.ssh('mkdir -p /output')
    server_app_dir = SETUP_DIR / 'server' / setup
    machine.scp_copy_dir(server_app_dir, '/app', direction='to')
    machine.scp_copy_dir(CERT_DIR, '/cert', direction='to')

    machine.ssh(r"sed -i 's/\r$//' /app/setup.sh")
    machine.ssh('chmod +x /app/setup.sh && /app/setup.sh')

def resetup_server(args):
    log.info(f"Re-setting up server (with args: {args})")
    name = f'{NAME}-{args.setup}'
    machine = DigitalOceanMachine(config=CONFIG, name=name, reserved_ip=RESERVED_IP, domain=DNS)
    if not machine.is_online():
        log.error("Server is not online")
        return
    __setup_server(machine, args.setup)
    log.info("Server re-setup completed")

def start_server(args):
    log.info(f"Starting server (with args: {args})")
    name = f'{NAME}-{args.setup}'
    machine = DigitalOceanMachine(config=CONFIG, name=name, domain=DNS, reserved_ip=RESERVED_IP)
    if machine.is_online():
        print("Server is already online")
    else:
        print("Start server")
        machine.start()
        log.info("Server started")
    __setup_server(machine, args.setup)
    print("Server setup completed")
    log.info("Server setup completed")


def stop_server(args):
    log.info(f"Stopping server (with args: {args})")
    name = f'{NAME}-{args.setup}'
    machine = DigitalOceanMachine(config=CONFIG, name=name, reserved_ip=RESERVED_IP, domain=DNS)
    machine.stop()
    log.info("Server stopped")


def destroy_server(args):
    log.info(f"Destroying server (with args: {args})")
    name = f'{NAME}-{args.setup}'
    machine = DigitalOceanMachine(config=CONFIG, name=name, reserved_ip=RESERVED_IP, domain=DNS)
    machine.destroy()
    log.info("Server destroyed")

def ssh_server(args):
    log.info(f"Running SSH command on server (with args: {args})")
    name = f'{NAME}-{args.setup}'
    machine = DigitalOceanMachine(config=CONFIG, name=name, reserved_ip=RESERVED_IP, domain=DNS)
    machine.ssh(args.cmd)
    log.info("SSH command run on server")


def get_server(setup):
    name = f'{NAME}-{setup}'
    return DigitalOceanMachine(config=CONFIG, name=name, reserved_ip=RESERVED_IP, domain=DNS)
