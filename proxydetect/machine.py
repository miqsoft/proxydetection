from pathlib import Path
import logging
log = logging.getLogger(__name__)


class Machine:
    name: str
    ip: str
    domain: str
    output_dir: Path
    app_dir: Path

    interface: str = 'eth0'

    def __init__(self, name: str, ip: str = None, domain: str = None, output_dir: Path = Path('/output'), app_dir: Path = Path('/app')):
        self.name = name
        self.ip = ip
        self.domain = domain
        self.output_dir = output_dir
        self.app_dir = app_dir

    def ssh(self, cmd: str):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def is_online(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def start_capture(self, filename: str):
        outputfile = self.output_dir / filename
        logfile = self.output_dir / f"tcpdump_{Path(filename).stem}.log"
        self.ssh(f"nohup sudo tcpdump not port 22 -i {self.interface} -w {outputfile.as_posix()} > {logfile.as_posix()} 2>&1 & disown")

    def stop_capture(self):
        self.ssh('sudo killall tcpdump')

    def __str__(self):
        return f"{self.name} ({self.ip} - {self.domain})"

    def __repr__(self):
        return str(self)
