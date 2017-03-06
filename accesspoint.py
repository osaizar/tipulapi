import os

DHCPD_CONF_FILE = "conf/dhcpd.conf"

DHCP_CONF = """subnet 192.168.55.0 netmask 255.255.255.0 {
 range 192.168.55.10 192.168.55.50;
 option broadcast-address 192.168.55.255;
 option routers 192.168.55.1;
 default-lease-time 600;
 max-lease-time 7200;
 option domain-name "local";
 option domain-name-servers 8.8.8.8, 8.8.4.4;
}"""

os.system("apt install hostapd isc-dhcp-server iptables-persistent -y")

file_dhcpd = open(DHCPD_CONF_FILE, 'w')
lines = file_dhcpd.read().split("\n")

for l in lines:
    if l == 'option domain-name "example.org"':
        file_dhcpd.write("#"+l+"\n")
    if l == 'option domain-name-servers ns1.example.org, ns2.example.org;'
        file_dhcpd.write("#"+l+"\n")
    if l == '#authoritative;'
        file_dhcpd.write("authoritative\n")
    else:
        file_dhcpd.write(l+"\n")

file_dhcpd.close()

file_dhcpd = open(DHCPD_CONF_FILE, 'a')
file_dhcpd.write(DHCP_CONF)
file_dhcpd.close()
