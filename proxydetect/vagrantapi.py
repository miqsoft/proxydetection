import contextlib
import vagrant
from pathlib import Path
import jinja2
import shutil
from proxydetect.machine import Machine
from pssh.clients import SSHClient
from subprocess import CalledProcessError

import logging
log = logging.getLogger(__name__)


def render_vagrantfile(template: Path, output: Path, result_dir: Path, base_dir: Path, client='default'):
    with open(template) as f:
        content = f.read()
        template = jinja2.Template(content)
        with open(output, 'w') as f:
            f.write(template.render(client=client, result_dir=result_dir.absolute().as_posix(), base_dir=base_dir.absolute().as_posix()))


class VagrantMachine(Machine):
    box: vagrant.Vagrant
    output_local: Path
    ssh_port: int
    disable_ssh: bool = False

    def __init__(self, vagrant_dir: Path, name: str, ip: str, run_dir, output_local, base_local, domain: str = None, app_remote: Path = Path('/app'), output_remote: Path = Path('/output'), recreate_vagrantfile: bool=False):
        super().__init__(name, ip, domain, output_remote, app_remote)
        client_name = vagrant_dir.name
        self.output_local = output_local
        if not (run_dir / 'Vagrantfile').exists() or recreate_vagrantfile:
            if recreate_vagrantfile:
                log.info(f"Recreating Vagrantfile for {client_name} due to flag")
            else:
                log.info(f"Rendering Vagrantfile for {client_name}")
            render_vagrantfile(vagrant_dir / 'Vagrantfile', run_dir / 'Vagrantfile', output_local, base_local, client_name)
        else:
            log.info(f"Vagrantfile already exists for {client_name}")
        self.box = vagrant.Vagrant(run_dir, quiet_stdout=True, quiet_stderr=True)
        try:
            self.ssh_port = self.box.port()
        except CalledProcessError as e:
            self.disable_ssh = True


    def ssh(self, cmd: str):
        if self.disable_ssh:
            print(f"SSH is disabled for {self.name}, due to halted or stopped")
        client = SSHClient(
            'localhost', user='vagrant', password='vagrant', port=self.ssh_port
        )
        host_output = client.run_command(cmd)
        print(f"{self.name}: {cmd}")
        for line in host_output.stdout:
            print(f'\t {line}')
        for line in host_output.stderr:
            print(f'\tX {line}')
        return host_output.exit_code


    def start(self):
        self.box.up()

    def stop(self):
        self.box.halt()

    def is_online(self):
        return self.box.status()[0].state == 'running'

    def destroy(self):
        self.box.destroy()

    def copy_output_file(self, file: str, dst_dir: Path):
        local_file = self.output_local / file
        dst_file = dst_dir / file
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        # copy local file to remote (both on same system)
        shutil.copy(local_file, dst_file)




