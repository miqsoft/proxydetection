from pathlib import Path

from proxydetect.vagrantapi import VagrantMachine
from proxydetect.config import BASE_DIR, RUN_DIR, SETUP_DIR

import logging
log = logging.getLogger(__name__)


class SetupDoesNotExist(Exception):
    pass

NAME = 'client'
IP = '127.0.0.1'

def initialize_machine(setup, run_dir=None, recreate=False):
    directory = SETUP_DIR / 'client' / setup
    if not directory.exists():
        raise SetupDoesNotExist(f"Setup {setup} does not exist.")

    if run_dir:
        run_dir = Path(run_dir)
        if not run_dir.exists():
            raise NotADirectoryError(f"Run directory {run_dir} does not exist.")
    else:
        run_dir = RUN_DIR / setup
        if not run_dir.exists():
            run_dir.mkdir(parents=False)
            log.info(f"Created run directory: {run_dir}")

    output_dir = run_dir / 'output'
    if not output_dir.exists():
        output_dir.mkdir(parents=False)
        log.info(f"Created output directory: {output_dir}")

    name = f'{NAME}-{setup}'

    return VagrantMachine(directory, name, IP, run_dir=run_dir, output_local=output_dir, base_local=BASE_DIR, recreate_vagrantfile=recreate)


def start_client(args):
    log.info(f"Starting client (with args: {args})")
    machine = initialize_machine(args.setup, args.run_dir, args.recreate)
    machine.start()
    log.info(f"Client started for setup: {args.setup}")


def stop_client(args):
    log.info(f"Stopping client (with args: {args})")
    machine = initialize_machine(args.setup)
    machine.stop()
    log.info(f"Client stopped for setup: {args.setup}")


def destroy_client(args):
    log.info(f"Destroying client (with args: {args})")
    machine = initialize_machine(args.setup)
    machine.destroy()
    log.info(f"Client destroyed for setup: {args.setup}")

def ssh_client(args):
    log.info(f"Running SSH command on client (with args: {args})")
    machine = initialize_machine(args.setup)
    machine.ssh(args.cmd)
    log.info(f"SSH command run on client for setup: {args.setup}")


def get_client(setup: str):
    return initialize_machine(setup)