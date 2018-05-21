#!/usr/bin/python

# This script configurates hostapd with a dhcp server and forwarding to the given interface
import os
import sys
from functions import *

def main():
    if not check_root():
        print "[!] You must run this script as root!"
        sys.exit(1)

    install_apt_dependencies('hostapd')
    configure_dhcpd()
    configure_ip_addr()
    configure_hostapd()
    configure_nat()

    print "[+] Starting services"
    os.system("ifconfig "+c.IN_INT+" "+c.STATIC_IP)
    os.system("service isc-dhcp-server start")

    print "[+] Done!"
    print "[+] To test the access point, run 'sudo /usr/sbin/hostapd /etc/hostapd/hostapd.conf'"


if __name__ == "__main__":
    main()
