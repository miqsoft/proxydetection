import vagrant

def __start_pcap_capture(box, vm, interface, outputfile):
    # sleep 1 is to ensure that the tcpdump process is started before the next command is run
    # found here: https://stackoverflow.com/questions/25331758/vagrant-ssh-c-and-keeping-a-background-process-running-after-connection-closed
    command = f"nohup sudo tcpdump -i {interface} -w {outputfile} > /vagrant/results/tcpdump_{vm}.log 2>&1 & sleep 1"
    print(f"Running command: {command} on {vm}")
    box.ssh(vm, command)

def __stop_pcap_capture(box, vm):
    box.ssh(vm, "sudo killall tcpdump")