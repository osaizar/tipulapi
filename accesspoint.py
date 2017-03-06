#!/usr/bin/python

import os

WIFI = True
IN_INT = "wlan0"
OUT_INT = "eth0"


# conf files
DHCPD_CONF_FILE = "/etc/dhcp/dhcpd.conf" # /etc/dhcp/dhcpd.conf
ISC_DHCP_SERVER_CONF_FILE = "/etc/default/isc-dhcp-server" # /etc/default/isc-dhcp-server
INT_CONF_FILE = "/etc/network/interfaces" # /etc/network/interfaces
HOSTAPD_CONF_FILE = "/etc/hostapd/hostapd.conf" # /etc/hostapd/hostapd.conf
DEF_HOSTAPD_CONF_FILE = "/etc/default/hostapd" # /etc/default/hostapd
INIT_HOSTAPD_CONF_FILE = "/etc/init.d/hostapd" # /etc/default/hostapd
SYSCTL_FILE = "/etc/sysctl.conf" # /etc/sysctl.conf


# conf parameters
DHCP_CONF = """
subnet 192.168.55.0 netmask 255.255.255.0 {
 range 192.168.55.10 192.168.55.50;
 option broadcast-address 192.168.55.255;
 option routers 192.168.55.1;
 default-lease-time 600;
 max-lease-time 7200;
 option domain-name "local";
 option domain-name-servers 8.8.8.8, 8.8.4.4;
}
"""

INT_CONF = """
iface """+IN_INT+"""" inet static
  address 192.168.55.1
  netmask 255.255.255.0
"""

HOSTAPD_CONF = """
interface="""+IN_INT+"""
# driver=rtl871xdrv (pi3)
ssid=tipulapi
country_code=US
hw_mode=g
channel=6
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=raspberry
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
wpa_group_rekey=86400
ieee80211n=1
wme_enabled=1
"""

print "[+] Installing hostapd, isc-dhcp-server and iptables-persistent..."

os.system("apt install hostapd isc-dhcp-server iptables-persistent -y")

print "[+] Configuring DHCP server..."

lines = open(DHCPD_CONF_FILE, 'r').read().split("\n")
file_dhcpd = open(DHCPD_CONF_FILE, 'w')

for l in lines:
    if l == 'option domain-name "example.org";':
        file_dhcpd.write("#"+l+"\n")
    elif l == 'option domain-name-servers ns1.example.org, ns2.example.org;':
        file_dhcpd.write("#"+l+"\n")
    elif l == '#authoritative;':
        file_dhcpd.write("authoritative;\n")
    else:
        file_dhcpd.write(l+"\n")

file_dhcpd.close()

file_dhcpd = open(DHCPD_CONF_FILE, 'a')
file_dhcpd.write(DHCP_CONF)
file_dhcpd.close()

print "[+] DHCP server configured"
print "[+] Enabling DHCP server on "+IN_INT

lines = open(ISC_DHCP_SERVER_CONF_FILE, 'r').read().split("\n")
file_isc = open(ISC_DHCP_SERVER_CONF_FILE, 'w')

for l in lines:
    if "INTERFACES" in l:
        file_isc.write('INTERFACES="'+IN_INT+'"\n')
    else:
        file_isc.write(l+"\n")

file_isc.close()

print "[+] Enabled"

print "[+] Setting static IP address for "+IN_INT

os.system("ifdown "+IN_INT)

lines = open(INT_CONF_FILE, 'r').read().split("\n")
file_int = open(INT_CONF_FILE, 'w')

int_lines = False
for l in lines:
    if "iface "+IN_INT in l and not int_lines:
        file_int.write(INT_CONF)
        int_lines = True
    elif int_lines:
        if "iface" in l:
            int_lines = False
            file_int.write(l+"\n")
    else:
        file_int.write(l+"\n")

file_int.close()

os.system("ifconfig "+IN_INT+" 192.168.55.1")

print "[+] Interface configured"

if WIFI:
    print "[+] Configuring hostapd"

    file_hostapd = open(HOSTAPD_CONF_FILE, 'w')
    file_hostapd.write(HOSTAPD_CONF+"\n")
    file_hostapd.close()


    file_hostapd = open(DEF_HOSTAPD_CONF_FILE, 'a')
    file_hostapd.write('DAEMON_CONF="'+HOSTAPD_CONF_FILE+'"\n')
    file_hostapd.close()


    lines = open(INIT_HOSTAPD_CONF_FILE, 'r').read().split("\n")
    file_hostapd = open(INIT_HOSTAPD_CONF_FILE, 'w')

    for l in lines:
        if "DAEMON_CONF=" in l:
            file_hostapd.write("DAEMON_CONF="+HOSTAPD_CONF_FILE+"\n")
        else:
            file_hostapd.write(l+"\n")

    file_hostapd.close()

    print "[+] Configured!"

print "[+] Configuring NAT"

file_sysctl= open(SYSCTL_FILE, 'a')
file_sysctl.write('net.ipv4.ip_forward=1 \n')
file_sysctl.close()

os.system('sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward "')

os.system("iptables -t nat -A POSTROUTING -o "+OUT_INT+" -j MASQUERADE")
os.system("iptables -A FORWARD -i "+OUT_INT+" -o "+IN_INT+" -m state --state RELATED,ESTABLISHED -j ACCEPT")
os.system("iptables -A FORWARD -i "+IN_INT+" -o "OUT_INT" -j ACCEPT")

os.system('sh -c "iptables-save > /etc/iptables/rules.v4"')

print "[+] NAT configured!"

print "[+] Starting services"

os.system("service isc-dhcp-server start")

print "[+] DONE!"
print "[+] To test the access point, run 'sudo /usr/sbin/hostapd /etc/hostapd/hostapd.conf'"
