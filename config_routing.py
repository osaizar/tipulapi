#!/usr/bin/python

# This script configurates the forwarding of a given interface
import os
import sys
from functions import *

def main():
    if not check_root():
        print "[!] You must run this script as root!"
        sys.exit(1)

    install_apt_dependencies('routing')
    configure_ip_addr()
    configure_dhcpd()
    configure_nat()

    print "[+] Starting services"
    os.system("ifconfig "+c.IN_INT+" "+c.STATIC_IP)
    os.system("service isc-dhcp-server start")
    print "[+] Done!"


if __name__ == "__main__":
    main()
