import yaml
from pathlib import Path
from proxydetect.client import get_client
from proxydetect.server import get_server
from proxydetect.relay import get_relay
from proxydetect.config import DATA_DIR
import argparse

import logging
log = logging.getLogger(__name__)


def run_experiment(args):
    log.info(f"Running experiment (with args: {args})")
    experiment_file = Path(args.file)
    if not args.out:
        out_dir = DATA_DIR / experiment_file.parent / experiment_file.stem
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f'use {out_dir.as_posix()} as output directory')
    else:
        out_dir = Path(args.out)

    if not experiment_file.exists():
        print(f"Experiment file {experiment_file} does not exist")
        return

    if not out_dir.is_dir():
        print(f"Output directory {out_dir} does not exist")
        return


    with open(experiment_file, 'r') as f:
        experiment = yaml.safe_load(f)

    client_setup = experiment.get('client', 'default')
    server_setup = experiment.get('server', 'default')
    relay_setup = None
    client = get_client(client_setup)
    server = get_server(server_setup)
    relay = None
    if not client.is_online():
        print(f"Client setup {client_setup} is not online")
        return
    if not server.is_online():
        print(f"Server setup {server_setup} is not online")
        return

    if relay_dict := experiment.get('relay', None):
        if 'local' not in relay_dict:
            print("for an relay it need to specified wheter its local or remote with local: true or false")
            return
        if relay_dict['local']:
            relay_setup = relay_dict.get('setup', 'default')
            relay = get_relay(relay_setup)
            if not relay.is_online():
                print(f"Relay setup {relay_setup} is not online")
                return
        else:
            relay_dns = relay_dict.get('dns', None)
            relay_ip = relay_dict.get('ip', None)
            raise NotImplementedError("Remote relay not implemented yet")
    else:
        # for ground truth pcaps
        pass

    # start pcap for all machines
    client.start_capture('client.pcap')
    server.start_capture('server.pcap')
    if relay:
        relay.start_pcap('relay.pcap')

    try:
        # run experiment
        commands = experiment.get('commands', [])
        connect_commands = commands.get('connect', None)
        traffic_commands = commands.get('traffic', None)

        if connect_commands:
            for cmd in connect_commands:
                operator = list(cmd.keys())[0]
                command = cmd[operator]
                if command == "WAIT":
                    input("Press Enter to continue...")
                elif operator == 'client':
                    client.ssh(command)
                elif operator == 'server':
                    server.ssh(command)
                elif operator == 'relay':
                    if relay:
                        relay.ssh(command)
                    else:
                        raise ValueError("Relay not specified in experiment file")

        if traffic_commands:
            for cmd in traffic_commands:
                operator = list(cmd.keys())[0]
                command = cmd[operator]
                if command == "WAIT":
                    input("Press Enter to continue...")
                elif operator == 'client':
                    client.ssh(command)
                elif operator == 'server':
                    server.ssh(command)
                elif operator == 'relay':
                    if relay:
                        relay.ssh(command)
                    else:
                        raise ValueError("Relay not specified in experiment file")
    except Exception as e:
        raise
    finally:
        # stop pcap for all machines
        client.stop_capture()
        server.stop_capture()
        if relay:
            relay.stop_capture()

    # download/copy pcaps
    pcap_dir = out_dir / 'pcaps'
    logs_dir = out_dir / 'logs'
    pcap_dir.mkdir(parents=False, exist_ok=True)
    logs_dir.mkdir(parents=False, exist_ok=True)

    # save ip from relay and server and save
    with open(out_dir/'ips.txt', 'w') as f:
        f.write(f"server_assigned: {server.get_ip()}\n")
        f.write(f"server_reserved: {server.reserved_ip}\n")
        if relay:
            f.write(f"relay_assigned: {relay.get_ip()}\n")
            f.write(f"relay_reserved: {relay.reserved_ip}\n")

    client.copy_output_file('client.pcap', pcap_dir)
    server.scp_copy_file('/output/server.pcap', (pcap_dir/'server.pcap').as_posix(), direction='from')
    if relay:
        relay.scp_copy_file('/output/relay.pcap', (pcap_dir/'relay.pcap').as_posix(), direction='from')

    client.copy_output_file('tcpdump_client.log', logs_dir)
    server.scp_copy_file('/output/tcpdump_server.log', (logs_dir/'tcpdump_server.log').as_posix(), direction='from')
    if relay:
        relay.scp_copy_file('/output/tcpdump_relay.log', (logs_dir/'tcpdump_relay.log').as_posix(), direction='from')

    if logs := experiment.get('logs', None):
        if 'client' in logs:
           for file in logs['client']:
               if client.ssh(f'test -e /output/{file}') == 0:
                   client.copy_output_file(file, logs_dir)
                   client.ssh(f'rm /output/{file}')
               else:
                     print(f"File {file} not found on client")
        if 'server' in logs:
            for file in logs['server']:
                if server.ssh(f'test -e /output/{file}') == 0:
                    server.scp_copy_file(f'/output/{file}', (logs_dir/f'{file}').as_posix(), direction='from')
                    server.ssh(f'rm /output/{file}')
                else:
                    print(f"File {file} not found on server")
        if 'relay' in logs:
            for file in logs['relay']:
                if relay.ssh(f'test -e /output/{file}') == 0:
                    relay.scp_copy_file(f'/output/{file}', (logs_dir/f'{file}').as_posix(), direction='from')
                    relay.ssh(f'rm /output/{file}')
                else:
                    print(f"File {file} not found on relay")


def run_experiments(args):
    directory = Path(args.directory)
    if not directory.is_dir():
        print(f"Directory {directory} does not exist")
        return

    for file in directory.iterdir():
        if file.suffix in ['.yaml', '.yml']:
            namespace = argparse.Namespace(file=file.as_posix(), out=None)
            run_experiment(namespace)
        else:
            print(f"Skipping {file} as it is not a yaml file")
        
    

    




