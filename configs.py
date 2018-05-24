# You can edit this file to configure the scripts.

""" BASIC OPTIONS """

SSID = "pi-wifi" # wifi name
PASS = "raspberry" # wifi password

""" ADVANCED OPTIONS """

IN_INT = "eth0" # interface where the traffic will enter from
OUT_INT = "wlan0" # interface where the traffic will exit frim

""" EVEN MORE ADVANCED OPTIONS, WATCH OUT """

NETWORK = "192.168.55.0"
MASK = "255.255.255.0"
BROADCAST = "192.168.55.255"
GATEWAY = "192.168.55.1"
DNS_SERVER = "8.8.8.8"

DHCP_START = "192.168.55.10"
DHCP_END =  "192.168.55.100"

STATIC_IP = "192.168.55.1"
STATIC_MASK = "255.255.255.0"
