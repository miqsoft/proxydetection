import vagrant
from pathlib import Path
import jinja2


def render_vagrantfile(template: Path, output: Path, result_dir: Path, base_dir: Path):
    with open(template) as f:
        content = f.read()
        template = jinja2.Template(content)
        with open(output, 'w') as f:
            f.write(template.render(result_dir=result_dir.absolute().as_posix(), base_dir=base_dir.absolute().as_posix()))


class VagrantBox:
    box: vagrant.Vagrant

    def __init__(self, path: Path):
        self.box = vagrant.Vagrant(path, quiet_stdout=True, quiet_stderr=True)

    def start_pcap(self, interface, outputfile, log: str = '/dev/null'):
        # sleep 1 is to ensure that the tcpdump process is started before the next command is run
        # found here: https://stackoverflow.com/questions/25331758/vagrant-ssh-c-and-keeping-a-background-process-running-after-connection-closed
        command = f"nohup sudo tcpdump -i {interface} -w {outputfile} > {log} 2>&1 & sleep 1"
        print(f"Running command: {command} on client")
        self.box.ssh('client', command)

    def stop_pcap(self):
        self.box.ssh("sudo killall tcpdump")

    def ssh(self, command):
        self.box.ssh('client', command)

    def __enter__(self):
        self.box.up()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.box.destroy()



