import argparse
import sys

from proxydetect.client import start_client, stop_client, destroy_client, ssh_client
from proxydetect.server import start_server, stop_server, destroy_server, ssh_server, resetup_server
from proxydetect.relay import start_relay, stop_relay, destroy_relay, ssh_relay
from proxydetect.experiment import run_experiment

from dotenv import load_dotenv
load_dotenv()

import logging
log = logging.getLogger(__name__)


def default_function(args):
    print("No function assigned. Showing help.")
    args.parser.print_help()
    sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Detects if a proxy is being used')
    subparsers = parser.add_subparsers(help='sub-command help')

    # Relay commands
    relay_parser = subparsers.add_parser('relay', help='relay related commands')
    relay_subparsers = relay_parser.add_subparsers(help='relay sub-command help')

    relay_start = relay_subparsers.add_parser('start', help='Starts the relay server')
    relay_start.add_argument('setup', type=str, help='setup/relay to use')
    relay_start.set_defaults(func=start_relay)

    relay_stop = relay_subparsers.add_parser('stop', help='Stops the relay server')
    relay_stop.add_argument('setup', type=str, help='setup/relay to use')
    relay_stop.set_defaults(func=stop_relay)

    relay_ssh = relay_subparsers.add_parser('ssh', help='SSH related commands')
    relay_ssh.add_argument('setup', type=str, help='setup/relay to use')
    relay_ssh.add_argument('cmd', help='SSH command to run')
    relay_ssh.set_defaults(func=ssh_relay)

    relay_destroy = relay_subparsers.add_parser('destroy', help='Destroys the relay server')
    relay_destroy.add_argument('setup', type=str, help='setup/relay to use')
    relay_destroy.set_defaults(func=destroy_relay)

    # Server commands
    server_parser = subparsers.add_parser('server', help='server related commands')
    server_subparsers = server_parser.add_subparsers(help='server sub-command help')

    server_resetup = server_subparsers.add_parser('resetup', help='Re-setups the server')
    server_resetup.add_argument('setup', type=str, nargs='?', default='default', help='setup to use (default: default)')
    server_resetup.set_defaults(func=resetup_server)

    server_start = server_subparsers.add_parser('start', help='Starts the server')
    server_start.add_argument('setup', type=str, nargs='?', default='default', help='setup to use (default: default)')
    server_start.set_defaults(func=start_server)

    server_stop = server_subparsers.add_parser('stop', help='Stops the server')
    server_stop.add_argument('setup', type=str, nargs='?', default='default', help='setup to use (default: default)')
    server_stop.set_defaults(func=stop_server)

    server_destroy = server_subparsers.add_parser('destroy', help='Destroys the server')
    server_destroy.add_argument('setup', type=str, nargs='?', default='default', help='setup to use (default: default)')
    server_destroy.set_defaults(func=destroy_server)

    server_ssh = server_subparsers.add_parser('ssh', help='SSH related commands')
    server_ssh.add_argument('setup', type=str, nargs='?', default='default', help='setup to use (default: default)')
    server_ssh.add_argument('cmd', help='SSH command to run')
    server_ssh.set_defaults(func=ssh_server)

    # Client commands
    client_parser = subparsers.add_parser('client', help='client related commands')
    client_subparsers = client_parser.add_subparsers(help='client sub-command help')

    client_start = client_subparsers.add_parser('start', help='Starts the client')
    client_start.add_argument('--setup', type=str, default='default', help='setup to use (default: default)')
    client_start.add_argument('--run-dir', type=str, help='directory to run the client in')
    client_start.add_argument('--recreate', action='store_true', help='recreate the Vagrantfile')
    client_start.set_defaults(func=start_client)

    client_stop = client_subparsers.add_parser('stop', help='Stops the client')
    client_stop.add_argument('setup', type=str, nargs='?', default='default', help='setup to use (default: default)')
    client_stop.set_defaults(func=stop_client)

    client_destroy = client_subparsers.add_parser('destroy', help='Destroys the client')
    client_destroy.add_argument('setup', type=str, nargs='?', default='default', help='setup to use (default: default)')
    client_destroy.set_defaults(func=destroy_client)

    client_ssh = client_subparsers.add_parser('ssh', help='SSH related commands')
    client_ssh.add_argument('setup', type=str, nargs='?', default='default', help='setup to use (default: default)')
    client_ssh.add_argument('cmd', help='SSH command to run')
    client_ssh.set_defaults(func=ssh_client)


    experiment = subparsers.add_parser('experiment', help='Experiment related commands')
    experiment.add_argument('file', type=str, help='experiment file')
    experiment.add_argument('--out', type=str, help='output directory')
    experiment.set_defaults(func=run_experiment)


    # Ensure a function is always executed, or show help if no function was provided
    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()





