from pathlib import Path
import vagrant
import subprocess
import jinja2


def __start_pcap_capture(box, vm, interface, outputfile):
    # sleep 1 is to ensure that the tcpdump process is started before the next command is run
    # found here: https://stackoverflow.com/questions/25331758/vagrant-ssh-c-and-keeping-a-background-process-running-after-connection-closed
    command = f"nohup sudo tcpdump -i {interface} -w {outputfile} > /vagrant/results/tcpdump_{vm}.log 2>&1 & sleep 1"
    print(f"Running command: {command} on {vm}")
    box.ssh(vm, command)
    
def __stop_pcap_capture(box, vm):
    box.ssh(vm, "sudo killall tcpdump")

def curl(box, vm, prot: str, host: str = '192.168.56.6', insecure: bool = True, http2: bool = False, http3: bool = False):
    command = 'curl' + ' -v'
    if insecure:
        command += ' --insecure'
    if http2:
        command += ' --http2'
    if http3:
        command += ' --http3'
    command += f' {prot}://{host}'
    print(f"Running command: {command}")
    box.ssh(vm, f'{command} > /vagrant/results/curl_{vm}.log 2>&1')

def curl_request(proxytype, proxytunnelprotocol, box):
    prot = 'https' if 'HTTPS' in proxytunnelprotocol else 'http'
    http2 = 'HTTP2' in proxytunnelprotocol or 'HTTPS2' in proxytunnelprotocol
    http3 = 'HTTP3' in proxytunnelprotocol or 'HTTPS3' in proxytunnelprotocol
    curl(box, "client", prot, http2=http2, http3=http3)

def custom_tcp_request(box):
    box.ssh("client", "python3 /vagrant/client/tcp.py")

def openvpn_connect(box, vm: str):
    box.ssh(vm, "sudo openvpn --config /vagrant/config/client.conf --daemon")

def _experiment(box, proxytype: str, proxytunnelprotocol: str, proxysoftware: str):
    __start_pcap_capture(box, "client", "eth1", "/vagrant/results/client.pcap")
    __start_pcap_capture(box, "proxy", "eth1", "/vagrant/results/proxy.pcap")
    __start_pcap_capture(box, "server", "eth1", "/vagrant/results/server.pcap")

    if proxysoftware == 'OpenVPN':
        openvpn_connect(box, "client")
    if 'HTTP' in proxytunnelprotocol:
        curl_request(proxytype, proxytunnelprotocol, box)
    if proxytunnelprotocol == 'TCP':
        custom_tcp_request(box)
        
    __stop_pcap_capture(box, "client")
    __stop_pcap_capture(box, "proxy")
    __stop_pcap_capture(box, "server")


EXPERIMENTS = [
    ('HTTP1', 'HTTP1', 'squid'),
    ('HTTP1', 'HTTP1', '3proxy'),
    ('HTTP1', 'HTTPS1', 'squid'),
    ('HTTP1', 'HTTPS1', '3proxy'),
    ('HTTP1', 'HTTPS2', 'squid'),
    ('HTTP1', 'HTTPS2', '3proxy'),
    ('HTTP1', 'HTTP2', 'squid'),
    ('HTTP1', 'HTTP2', '3proxy'),
    ('HTTP1', 'HTTP3', '3proxy'), # todo: test
    ('HTTP1', 'TCP', '3proxy'),
    ('OpenVPN', 'HTTP1', 'OpenVPN'),
]


def main():
    experiments = [EXPERIMENTS[-2]]

    for proxytype, proxytunnelprotocol, proxysoftware in experiments:
        subpath = f'{proxytype}/{proxytunnelprotocol}/{proxysoftware}'
        basedir = Path(__file__).parent.parent
        vg_dir = basedir/'vm'/subpath
        outputdir = basedir/'pcaps'/subpath
        outputdir.mkdir(parents=True, exist_ok=True)
        # clear the output directory
        for file in outputdir.iterdir():
            file.unlink()

        template = vg_dir/'template'/'Vagrantfile'

        # render the Vagrantfile template
        with open(template, 'r') as f:
            template = jinja2.Template(f.read())
            file = vg_dir/'Vagrantfile'
            with open(file, 'w') as f:
                f.write(template.render(result_dir=outputdir.absolute().as_posix(), base_dir=basedir.absolute().as_posix()))

        box = vagrant.Vagrant(
            root=vg_dir.as_posix(),
            quiet_stdout=False,
            quiet_stderr=False
        )
        box.up()

        try:
            _experiment(box, proxytype, proxytunnelprotocol, proxysoftware)
        except subprocess.CalledProcessError as e:
            print("An error occurred: stopping all machines")
            print(e)
        finally:
            pass
            #box.destroy()


if __name__ == '__main__':
    main()
