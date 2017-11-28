#!/usr/bin/python

# This script configurates hostapd with a dhcp server and forwarding to the given interface

import os
import sys
from configurables import DHCPD, DHCP_ENABLE, INTERFACES, INITD_HOSTAPD, DEF_HOSTAPD, HOSTAPD, SYSCTL
import configs as c

def main():
    if not check_root():
        print "[!] You must run this script as root!"
        sys.exit(1)

    install_apt_dependencies()
    configure_dhcpd()
    configure_hostapd()
    configure_nat()

    print "[+] Starting services"
    os.system("service isc-dhcp-server start")

    print "[+] Done!"
    print "[+] To test the access point, run 'sudo /usr/sbin/hostapd /etc/hostapd/hostapd.conf'"

def check_root():
    if os.geteuid() != 0:
        return False
    else:
        return True

def install_apt_dependencies():
    print "[+] Installing hostapd, isc-dhcp-server and iptables-persistent..."
    os.system("apt update")
    os.system("apt install hostapd isc-dhcp-server iptables-persistent -y")
    print "[+] done"

def configure_dhcpd():
    print "[+] Configurig dhcp server..."
    DHCPD.set_attrs([c.NETWORK, c.MASK, c.DHCP_START, c.DHCP_END, c.BROADCAST, c.GATEWAY, c.DNS_SERVER])
    DHCPD.to_file()
    print "[+] Configuration writen to: "+DHCPD.file
    print "[+] Enabling DHCP server on "+c.IN_INT
    DHCP_ENABLE.set_attrs([c.IN_INT])
    DHCP_ENABLE.to_file()
    print "[+] Enabled"

def configure_ip_addr():
    print "[+] Setting static IP address for "+c.IN_INT
    os.system("ifdown "+c.IN_INT)
    INTERFACES.set_attrs([c.IN_INT, c.STATIC_IP, c.STATIC_MASK])
    INTERFACES.to_file()
    os.system("ifconfig "+c.IN_INT+" "+c.STATIC_IP)
    print "[+] IP address configured"

def configure_hostapd():
    print "[+] Configuring hostapd"
    HOSTAPD.set_attrs([c.IN_INT, c.SSID, c.PASS])
    HOSTAPD.to_file()
    print "[+] Hostapd configuration written"

    DEF_HOSTAPD.to_file()
    print "[+] Hostapd pointed into configuration file"

    print "[+] Creating init.d service..."
    INITD_HOSTAPD.to_file()
    print "[+] Service created"
    print "[+] Hostapd configured"

def configure_nat():
    print "[+] Configuring NAT"
    print "[+] Enabling forwarding..."
    SYSCTL.to_file()
    print "[+] Enabled"

    print "[+] Adding NAT rules..."
    os.system('sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward "')

    os.system("iptables -t nat -A POSTROUTING -o "+c.OUT_INT+" -j MASQUERADE")
    os.system("iptables -A FORWARD -i "+c.OUT_INT+" -o "+c.IN_INT+" -m state --state RELATED,ESTABLISHED -j ACCEPT")
    os.system("iptables -A FORWARD -i "+c.IN_INT+" -o "+c.OUT_INT+" -j ACCEPT")

    os.system('sh -c "iptables-save > /etc/iptables/rules.v4"')

    print "[+] NAT configured!"


if __name__ == "__main__":
    main()
