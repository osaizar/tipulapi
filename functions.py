import os
import sys
from configurables import DHCPD, DHCP_ENABLE, INTERFACES, INITD_HOSTAPD, DEF_HOSTAPD, HOSTAPD, SYSCTL
import configs as c

def check_root():
    if os.geteuid() != 0:
        return False
    else:
        return True

def install_apt_dependencies(option):
    if option == "routing":
        install = "isc-dhcp-server iptables-persistent"
    elif option == "bridge":
        install = "bridge-utils"
    else: # hostapd
        install = "hostapd isc-dhcp-server iptables-persistent"

    print "[+] Installing "+install+"..."
    os.system("apt update")
    os.system("apt install "+install+" -y")
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
    INITD_HOSTAPD.set_attrs(["DAEMON_CONF="+HOSTAPD.file])
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

def configure_bridge():
    print "[+] Configuring a bridge"
    print "[+] Enabling forwarding..."
    SYSCTL.to_file()
    os.system('sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward "')
    print "[+] Enabled"

    print "[+] Configuring the bridge"
    BRIDGE.set_attrs([c.IN_INT, c.OUT_INT])
    BRIDGE.to_file()
    os.system("ifup br0")
    print "[+] Configured!"
