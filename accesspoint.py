#!/usr/bin/python

import os

HOSTAPD = True
WPA = False

IN_INT = "wlan0"
OUT_INT = "eth0"

WPA_NAME = ""
WPA_PASSWORD = ""


# conf files
DHCPD_FILE = "/etc/dhcp/dhcpd.conf" # /etc/dhcp/dhcpd.conf
ISC_DHCP_FILE = "/etc/default/isc-dhcp-server" # /etc/default/isc-dhcp-server
INT_FILE = "/etc/network/interfaces" # /etc/network/interfaces
MAIN_HOSTAPD_FILE = "/etc/hostapd/hostapd.conf" # /etc/hostapd/hostapd.conf
DEF_HOSTAPD_FILE = "/etc/default/hostapd" # /etc/default/hostapd
INIT_HOSTAPD_FILE = "/etc/init.d/hostapd" # /etc/default/hostapd
SYSCTL_FILE = "/etc/sysctl.conf" # /etc/sysctl.conf
WPA_FILE = "/etc/wpa_supplicant/wpa_supplicant.conf"

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
iface """+IN_INT+""" inet static
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

WPA_CONF = '''
network={
ssid="'''+WPA_NAME+'''"
psk="'''+WPA_PASSWORD+'''"
proto=RSN
key_mgmt=WPA-PSK
pairwise=CCMP
auth_alg=OPEN
}
'''

print "[+] Installing hostapd, isc-dhcp-server and iptables-persistent..."

os.system("apt install hostapd isc-dhcp-server iptables-persistent -y")

print "[+] Configuring DHCP server..."

lines = open(DHCPD_FILE, 'r').read().split("\n")
file_dhcpd = open(DHCPD_FILE, 'w')

auth_written = False;
for l in lines:
    if l == 'option domain-name "example.org";':
        file_dhcpd.write("#"+l+"\n")
    elif l == 'option domain-name-servers ns1.example.org, ns2.example.org;':
        file_dhcpd.write("#"+l+"\n")
    elif l == '#authoritative;':
        file_dhcpd.write("authoritative;\n")
        auth_written = True
    else:
        file_dhcpd.write(l+"\n")

if not auth_written:
    file_dhcpd.write("authoritative;\n")

file_dhcpd.close()

file_dhcpd = open(DHCPD_FILE, 'a')
file_dhcpd.write(DHCP_CONF)
file_dhcpd.close()

print "[+] DHCP server configured"
print "[+] Enabling DHCP server on "+IN_INT

lines = open(ISC_DHCP_FILE, 'r').read().split("\n")
file_isc = open(ISC_DHCP_FILE, 'w')

int_written = False
for l in lines:
    if "INTERFACES" in l:
        file_isc.write('INTERFACES="'+IN_INT+'"\n')
        int_written = True
    else:
        file_isc.write(l+"\n")

if not int_written:
    file_isc.write('INTERFACES="'+IN_INT+'"\n')

file_isc.close()

print "[+] Enabled"

print "[+] Setting static IP address for "+IN_INT

os.system("ifdown "+IN_INT)

lines = open(INT_FILE, 'r').read().split("\n")
file_int = open(INT_FILE, 'w')

int_lines = False
for l in lines:
    if "iface "+IN_INT in l and not int_lines:
        file_int.write(INT_CONF+"\n")
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

if HOSTAPD:
    print "[+] Configuring hostapd"

    file_hostapd = open(MAIN_HOSTAPD_FILE, 'w')
    file_hostapd.write(HOSTAPD_CONF+"\n")
    file_hostapd.close()


    file_hostapd = open(DEF_HOSTAPD_FILE, 'a')
    file_hostapd.write('DAEMON_CONF="'+MAIN_HOSTAPD_FILE+'"\n')
    file_hostapd.close()


    lines = open(INIT_HOSTAPD_FILE, 'r').read().split("\n")
    file_hostapd = open(INIT_HOSTAPD_FILE, 'w')

    daemon_written = False

    for l in lines:
        if "DAEMON_CONF=" in l:
            daemon_written = True
            file_hostapd.write("DAEMON_CONF="+MAIN_HOSTAPD_FILE+"\n")
        else:
            file_hostapd.write(l+"\n")

    if not daemon_written:
        file_hostapd.write("DAEMON_CONF="+MAIN_HOSTAPD_FILE+"\n")

    file_hostapd.close()

    print "[+] Configured!"

if WPA:
    print "[+] Configuring wpa connection to "+WPA_NAME+" network"

    file_wpa = open(WPA_FILE, 'a')
    file_wpa.write(WPA_CONF)
    file_wpa.close()

    print "[+] Done!"


print "[+] Configuring NAT"

file_sysctl= open(SYSCTL_FILE, 'a')
file_sysctl.write('net.ipv4.ip_forward=1 \n')
file_sysctl.close()

os.system('sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward "')

os.system("iptables -t nat -A POSTROUTING -o "+OUT_INT+" -j MASQUERADE")
os.system("iptables -A FORWARD -i "+OUT_INT+" -o "+IN_INT+" -m state --state RELATED,ESTABLISHED -j ACCEPT")
os.system("iptables -A FORWARD -i "+IN_INT+" -o "+OUT_INT+" -j ACCEPT")

os.system('sh -c "iptables-save > /etc/iptables/rules.v4"')

print "[+] NAT configured!"

print "[+] Starting services"

os.system("service isc-dhcp-server start")

print "[+] DONE!"

if HOSTAPD:
    print "[+] To test the access point, run 'sudo /usr/sbin/hostapd /etc/hostapd/hostapd.conf'"

if WPA:
    print "[+] Now yo can connect to "+WPA_NAME
