import os

# conf files
DHCPD_CONF_FILE = "conf/dhcpd.conf" # /etc/dhcp/dhcpd.conf
ISC_DHCP_SERVER_CONF_FILE = "conf/isc-dhcp-server" # /etc/default/isc-dhcp-server
INT_CONF_FILE = "conf/interfaces" # /etc/network/interfaces
HOSTAPD_CONF_FILE = "conf/hostapd.conf" # /etc/hostapd/hostapd.conf
DEF_HOSTAPD_CONF_FILE = "conf/hostapd" # /etc/default/hostapd
INIT_HOSTAPD_CONF_FILE = "conf/init_hostapd" # /etc/default/hostapd
SYSCTL_FILE = "conf/sysctl.conf" # /etc/sysctl.conf

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
DHCP_INT = "wlan0"

INT_CONF = """
iface """+DHCP_INT+"""" inet static
  address 192.168.55.1
  netmask 255.255.255.0
"""

HOSTAPD_CONF = """
interface="""+DHCP_INT+"""
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
print "[+] Enabling DHCP server on "+DHCP_INT

lines = open(ISC_DHCP_SERVER_CONF_FILE, 'r').read().split("\n")
file_isc = open(ISC_DHCP_SERVER_CONF_FILE, 'w')

for l in lines:
    if "INTERFACES" in l:
        file_isc.write('INTERFACES="+'DHCP_INT'+"\n')
    else:
        file_isc.write(l+"\n")

file_isc.close()

print "[+] Enabled"

print "[+] Setting static IP address for "+DHCP_INT

os.system("ifdown "+DHCP_INT)

lines = open(INT_CONF_FILE, 'r').read().split("\n")
file_int = open(INT_CONF_FILE, 'w')

int_lines = False
for l in lines:
    if "iface "+DHCP_INT in l and not int_lines:
        file_int.write(INT_CONF)
        int_lines = True
    elif int_lines:
        if "iface" in l:
            int_lines = False
            file_int.write(l+"\n")
    else:
        file_int.write(l+"\n")

file_int.close()

os.system("ifconfig "+DHCP_INT+" 192.168.55.1")

print "[+] Interface configured"
print "[+] Configuring hostapd"

file_hostapd = open(HOSTAPD_CONF_FILE, 'w')
file_hostapd.write(HOSTAPD_CONF)
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
file_sysctl.write('net.ipv4.ip_forward=1')
file_sysctl.close()

os.system('sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward "')

os.system("iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE")
os.system("iptables -A FORWARD -i eth0 -o "+DHCP_CONF+" -m state --state RELATED,ESTABLISHED -j ACCEPT")
os.system("iptables -A FORWARD -i "+DHCP_CONF+" -o eth0 -j ACCEPT")

os.system('sh -c "iptables-save > /etc/iptables/rules.v4"')

print "[+] NAT configured!"

print "[+] DONE!"
print "[+] To test the access point, run 'sudo /usr/sbin/hostapd /etc/hostapd/hostapd.conf'"
