import digitalocean
import os
import time
from contextlib import contextmanager

from dotenv import load_dotenv
load_dotenv()
DIGITAL_OCEAN_TOKEN = os.getenv('DIGITAL_OCEAN_TOKEN')


@contextmanager
def create_droplet(name: str, ram: int = 4, cpu: int = 2, region: str = 'fra1'):
    print(DIGITAL_OCEAN_TOKEN)
    manager = digitalocean.Manager(token=DIGITAL_OCEAN_TOKEN)
    keys = manager.get_all_sshkeys()

    droplet = digitalocean.Droplet(
        token=DIGITAL_OCEAN_TOKEN,
        name=name,
        region=region,
        image='ubuntu-24-04-x64',
        size_slug=f's-{cpu}vcpu-{ram}gb',
        backups=False,
        keys=keys,
    )

    try:
        droplet.create()
        print("Droplet created, waiting to be online...")
        seconds_waited = 0
        while seconds_waited < 120:
            droplet.load()
            if droplet.status == 'active':
                print("\nDroplet is online.")
                break
            print(f"\rWaited seconds: {seconds_waited}", end="")
            time.sleep(1)
            seconds_waited += 1
        yield droplet

    finally:
        droplet.destroy()
        print("\nDroplet destroyed.")


if __name__ == '__main__':

    with create_droplet('test-droplet') as droplet:
        # print droplet ip
        print(f"Droplet IP: {droplet.ip_address}")
        # wait for input to destroy the droplet
        input("Press Enter to destroy the droplet...")
