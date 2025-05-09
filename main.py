from pyfiglet import Figlet
from colorama import Fore
import re
import subprocess
from optparse import OptionParser
import random


"""
    Usage: This tool changes the MAC address of machines. The usage is as follows:

    The -i / --interface parameters are required and must be specified.
    Example: sudo python -i eth0
             sudo python -interface eth0

    The -m / --mac parameter is optional. If not provided, a random MAC address will be assigned.
    Example: sudo python -i eth0 -m 00:a2:b2:22:11:c2
             sudo python -interface eth0 -mac 00:a2:b2:22:11:c2
             sudo python -i eth0 -mac 00:a2:b2:22:11:c2
             sudo python -interface eth0 -m 00:a2:b2:22:11:c2
"""


class Mac_Changer():
    network_interfaces = [
        "eth0", "eth1", "enp0s3", "eno1",
        "wlan0", "wlan1", "wlp2s0", "wlp3s0"
    ]

    def __init__(self):

        figlet = Figlet(font='slant')
        print(Fore.CYAN + figlet.renderText('ChangerMac'))

        print(Fore.RED + f'''
-------------------------------------------------------     
|                                                     |
|                     AUTHOR:CHARON                   |
|          github:{Fore.BLUE}https://github.com/mhmtylpr44{Fore.RED}       |
|                                                     |
-------------------------------------------------------       

        ''')

        self.mac_address = ""
        self.interface = ""
        self.get_interface_and_mac_address()

    def get_interface_and_mac_address(self):

        parser = OptionParser()
        parser.add_option('-i', '--interface', dest='interface', help=
        '''
        Specify the network interface to use (e.g., eth0, wlan0, enp3s0).
        You can list available interfaces using 'ip link' or 'ifconfig'.
        This option is required if you want to bind the operation to a specific interface.
        ''')
        parser.add_option('-m', '--mac', dest='mac_address', help='''
Specify the MAC address to use (e.g., 00:1A:2B:3C:4D:5E).
The address must be in the standard format (XX:XX:XX:XX:XX:XX),
where XX is a pair of hexadecimal digits (0-9, A-F).
If not provided, a random MAC address will be generated.
Ensure the MAC address is valid for your network configuration.       
        ''')

        (options, arguments) = parser.parse_args()

        self.interface = options.interface
        self.mac_address = options.mac_address

        if self.interface in self.network_interfaces:
            if self.mac_address == None:
                def generate_random_mac():
                    mac = [0x02, random.randint(0x00, 0x7f)] + [random.randint(0x00, 0xff) for _ in range(4)]
                    return ':'.join(f'{octet:02x}' for octet in mac)

                self.mac_address = generate_random_mac()
                self.change_to_mac_address()

            else:
                self.change_to_mac_address()

        else:
            print(
                Fore.RED + "Specified network interface not found. Please provide a valid interface name (e.g., 'eth0' or 'wlan0').")

    def change_to_mac_address(self):

        subprocess.call(['ifconfig', self.interface, 'down'])
        subprocess.call(['ifconfig', self.interface, 'hw', 'ether', self.mac_address])
        subprocess.call(['ifconfig', self.interface, 'up'])

        ifconfig = subprocess.check_output(['ifconfig', self.interface])
        mac_int_adress = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", str(ifconfig))

        if str(mac_int_adress.group(0)) == str(self.mac_address):
            print(Fore.GREEN + 'Changed to Mac Address')
        else:
            print(Fore.RED + 'Please check your input and try again. If the problem persists, contact support.')


if __name__ == '__main__':
    Mac_Changer()
