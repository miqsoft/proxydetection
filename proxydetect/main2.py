import time
from proxydetect.digitaloceanapi import create_droplet, create_droplets
from vagrantapi import VagrantBox, render_vagrantfile
from pathlib import Path
import os
from proxydetect.config import SERVER_DROPLET, PROXY_DROPLET, DNS, RESERVED_IP, CLIENT_VAGRANTDIR_MAP

from dotenv import load_dotenv
load_dotenv()

PROXY_DNS = DNS['proxy']
SERVER_DNS = DNS['server']
PROXY_IP = RESERVED_IP['proxy']
SERVER_IP = RESERVED_IP['server']
BASE_DIR = Path(os.getenv('BASE_DIR'))
RUN_DIR = BASE_DIR / 'run'
CERT_DIR = BASE_DIR / 'cert'



class TrafficCapture:
    def __init__(self, obj, interface, output_filename, log=None):
        self.obj = obj
        self.interface = interface
        self.output_file = f'/output/{output_filename}'
        self.log = log

    def __enter__(self):
        self.obj.start_pcap(self.interface, self.output_file, log=self.log)
        print(f'{self.obj.name}: capture started')
        return self.obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.obj.stop_pcap()
        print(f'{self.obj.name}: capture stopped')



def _test_client_server(server: str, output_dir: Path):
    server_app_dir = BASE_DIR/'server'/server
    render_vagrantfile(BASE_DIR/CLIENT_VAGRANTDIR_MAP[server], RUN_DIR/'Vagrantfile', output_dir, BASE_DIR)
    return
    with VagrantBox(RUN_DIR) as client:
        with create_droplet(SERVER_DROPLET) as server:
            try:
                server.ssh('apt update && apt install -y tcpdump')
                server.ssh('mkdir -p /app')
                server.ssh('mkdir -p /cert')
                server.ssh('mkdir -p /output')
                server.scp_copy_dir(server_app_dir, '/app', direction='to')
                server.scp_copy_dir(CERT_DIR, '/cert', direction='to')
                server.ssh(r"sed -i 's/\r$//' /app/setup.sh")
                server.ssh('chmod +x /app/setup.sh && /app/setup.sh')

                # test http1 (without DNS)
                with TrafficCapture(client, 'eth0', 'http1_client.pcap', log='/output/tcpdump_http1_client.log'):
                    with TrafficCapture(server, 'eth0', 'http1_server.pcap', log='/output/tcpdump_http1_server.log'):
                        command = f'curl -v http://{SERVER_IP}:8000 > /output/http1_client.log 2>&1'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test http1 (with DNS)
                with TrafficCapture(client, 'eth0', 'http1dns_client.pcap', log='/output/tcpdump_http1dns_client.log'):
                    with TrafficCapture(server, 'eth0', 'http1dns_server.pcap', log='/output/tcpdump_http1dns_server.log'):
                        command = f'curl -v http://{SERVER_DNS}:8000 > /output/http1dns_client.log 2>&1'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test http2 (without DNS)
                with TrafficCapture(client, 'eth0', 'http2_client.pcap', log='/output/tcpdump_http2_client.log'):
                    with TrafficCapture(server, 'eth0', 'http2_server.pcap', log='/output/tcpdump_http2_server.log'):
                        command = f'curl --http2 -v http://{SERVER_IP}:8001 > /output/http2_client.log 2>&1'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test http2 (with DNS)
                with TrafficCapture(client, 'eth0', 'http2dns_client.pcap', log='/output/tcpdump_http2dns_client.log'):
                    with TrafficCapture(server, 'eth0', 'http2dns_server.pcap', log='/output/tcpdump_http2dns_server.log'):
                        command = f'curl --http2 -v http://{SERVER_DNS}:8001 > /output/http2dns_client.log 2>&1'
                        print(f'client: run - {command}')
                        client.ssh(command)


                # test https1 (without DNS)
                with TrafficCapture(client, 'eth0', 'https1_client.pcap', log='/output/tcpdump_https1_client.log'):
                    with TrafficCapture(server, 'eth0', 'https1_server.pcap', log='/output/tcpdump_https1_server.log'):
                        command = f'curl -k -v https://{SERVER_IP}:4000 > /output/https1_client.log 2>&1'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test https1 (with DNS)
                with TrafficCapture(client, 'eth0', 'https1dns_client.pcap', log='/output/tcpdump_https1dns_client.log'):
                    with TrafficCapture(server, 'eth0', 'https1dns_server.pcap', log='/output/tcpdump_https1dns_server.log'):
                        command = f'curl -k -v https://{SERVER_DNS}:4000 > /output/https1dns_client.log 2>&1'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test https2 (without DNS)
                with TrafficCapture(client, 'eth0', 'https2_client.pcap', log='/output/tcpdump_https2_client.log'):
                    with TrafficCapture(server, 'eth0', 'https2_server.pcap', log='/output/tcpdump_https2_server.log'):
                        command = f'curl -k --http2 -v https://{SERVER_IP}:4001 > /output/https2_client.log 2>&1'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test https2 (with DNS)
                with TrafficCapture(client, 'eth0', 'https2dns_client.pcap', log='/output/tcpdump_https2dns_client.log'):
                    with TrafficCapture(server, 'eth0', 'https2dns_server.pcap', log='/output/tcpdump_https2dns_server.log'):
                        command = f'curl -k --http2 -v https://{SERVER_DNS}:4001 > /output/https2dns_client.log 2>&1'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test http3 (without DNS)
                # todo:
                with TrafficCapture(client, 'eth0', 'http3_client.pcap', log='/output/tcpdump_http3_client.log'):
                    with TrafficCapture(server, 'eth0', 'http3_server.pcap', log='/output/tcpdump_http3_server.log'):
                        command = f'python3 /app/http3_client.py https://{SERVER_IP}:8002'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test http3 (with DNS)
                with TrafficCapture(client, 'eth0', 'http3dns_client.pcap', log='/output/tcpdump_http3dns_client.log'):
                    with TrafficCapture(server, 'eth0', 'http3dns_server.pcap', log='/output/tcpdump_http3dns_server.log'):
                        command = f'python3 /app/http3_client.py https://{SERVER_DNS}:8002'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test ws (without DNS)
                with TrafficCapture(client, 'eth0', 'ws_client.pcap', log='/output/tcpdump_ws_client.log'):
                    with TrafficCapture(server, 'eth0', 'ws_server.pcap', log='/output/tcpdump_ws_server.log'):
                        command = f'python3 /app/ws_client.py ws://{SERVER_IP}:8100 false'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test ws (with DNS)
                with TrafficCapture(client, 'eth0', 'wsdns_client.pcap', log='/output/tcpdump_wsdns_client.log'):
                    with TrafficCapture(server, 'eth0', 'wsdns_server.pcap', log='/output/tcpdump_wsdns_server.log'):
                        command = f'python3 /app/ws_client.py ws://{SERVER_DNS}:8100 false'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test wss (without DNS)
                with TrafficCapture(client, 'eth0', 'wss_client.pcap', log='/output/tcpdump_wss_client.log'):
                    with TrafficCapture(server, 'eth0', 'wss_server.pcap', log='/output/tcpdump_wss_server.log'):
                        command = f'python3 /app/ws_client.py wss://{SERVER_IP}:8101 true'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test wss (with DNS)
                with TrafficCapture(client, 'eth0', 'wssdns_client.pcap', log='/output/tcpdump_wssdns_client.log'):
                    with TrafficCapture(server, 'eth0', 'wssdns_server.pcap', log='/output/tcpdump_wssdns_server.log'):
                        command = f'python3 /app/ws_client.py wss://{SERVER_DNS}:8101 true'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test ssh (without DNS)
                with TrafficCapture(client, 'eth0', 'ssh_client.pcap', log='/output/tcpdump_ssh_client.log'):
                    with TrafficCapture(server, 'eth0', 'ssh_server.pcap', log='/output/tcpdump_ssh_server.log'):
                        command = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i /app/id_rsa root@{SERVER_IP} "echo ssh test" > /output/ssh_client.log 2>&1'
                        print(f'client: run - {command}')
                        client.ssh(command)

                # test ssh (with DNS)
                with TrafficCapture(client, 'eth0', 'sshdns_client.pcap', log='/output/tcpdump_sshdns_client.log'):
                    with TrafficCapture(server, 'eth0', 'sshdns_server.pcap', log='/output/tcpdump_sshdns_server.log'):
                        command = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i /app/id_rsa root@{SERVER_DNS} "echo ssh test" > /output/sshdns_client.log 2>&1'
                        print(f'client: run - {command}')
                        client.ssh(command)

            except Exception as e:
                print('exception occurred')
                raise e
            finally:
                server.scp_copy_dir('/output/', output_dir, direction='from')
                # copy all files from within output_dir/output to output_dir and remove output_dir/output
                output_subdir = output_dir / 'output'
                if output_subdir.is_dir():
                    # Collect file paths first
                    files = list(output_subdir.iterdir())

                    # Rename files outside of iteration
                    for file in files:
                        file.rename(output_dir / file.name)

                    # Remove the now-empty directory
                    output_subdir.rmdir()
                input('Press enter to continue')


def run_experiment(server: str, relay: str = None, relay_local: bool = True):
    result_dir = BASE_DIR/'results'/f'{server}_{relay}'
    result_dir.mkdir(parents=True, exist_ok=True)
    relay_app_dir = BASE_DIR/'relay'/relay
    server_app_dir = BASE_DIR/'server'/server
    render_vagrantfile(BASE_DIR/CLIENT_VAGRANTDIR_MAP[server], RUN_DIR/'Vagrantfile', result_dir, BASE_DIR)

    with VagrantBox(RUN_DIR) as client:
        with create_droplet(SERVER_DROPLET) as server:
            with create_droplet(PROXY_DROPLET) as proxy:
                proxy.ssh('mkdir -p /app')
                proxy.ssh('mkdir -p /cert')
                proxy.ssh('mkdir -p /output')
                proxy.scp_copy_dir(relay_app_dir, '/app', direction='to')
                proxy.scp_copy_dir(CERT_DIR, '/cert', direction='to')

                server.ssh('mkdir -p /app')
                server.ssh('mkdir -p /cert')
                server.ssh('mkdir -p /output')
                server.scp_copy_dir(server_app_dir, '/app', direction='to')
                server.scp_copy_dir(CERT_DIR, '/cert', direction='to')

                # remove crlf from scripts (for windows)
                proxy.ssh(r"sed -i 's/\r$//' /app/setup.sh")
                proxy.ssh("chmod +x /app/setup.sh && /app/setup.sh > /output/proxy_setup.log 2>&1")
                server.ssh(r"sed -i 's/\r$//' /app/setup.sh")
                server.ssh('chmod +x /app/setup.sh && /app/setup.sh > /output/server_setup.log 2>&1')

                client.start_pcap('eth0', '/vagrant/results/client.pcap', log='/vagrant/results/tcpdump_client.log')
                print('client: capture started')
                proxy.start_pcap('eth0', '/output/proxy.pcap', log='/output/tcpdump_proxy.log')
                print('proxy: capture started')
                server.start_pcap('eth0', '/output/server.pcap', log='/output/tcpdump_server.log')
                print('server: capture started')

                # experiment part: this part changes all other stay always the same (only that we select what we want to start (so only server,client,proxy or two of them or all)
                print(f'client: run - export http_proxy=http://{PROXY_IP}:3128 && curl -v http://{SERVER_IP}')
                client.ssh(f'export http_proxy=http://{PROXY_IP}:3128 && curl -v http://{SERVER_IP}')
                print('client: request sent')
                # experiment part end:

                client.stop_pcap()
                print('client: capture stopped')
                proxy.stop_pcap()
                print('proxy: capture stopped')
                server.stop_pcap()
                print('server: capture stopped')

                proxy.scp_copy_file('/output/*', result_dir.as_posix(), direction='from')
                server.scp_copy_file('/output/*', result_dir.as_posix(), direction='from')



if __name__ == '__main__':
    _test_client_server('default', BASE_DIR/'test')
    # with VagrantBox(RUN_DIR) as client:
    #     input('Press enter to continue')





