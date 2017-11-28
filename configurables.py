from configurable import Configurable

DHCPD_CONF = """
subnet %NETWORK% netmask %MASK% {
 range %STARTADDR% %ENDADDR%;
 option broadcast-address %BROADCAST%;
 option routers %GATEWAY%;
 default-lease-time 600;
 max-lease-time 7200;
 option domain-name "local";
 option domain-name-servers %DNSSERVER%;
}
"""

DHCPD = Configurable(DHCPD_CONF,
                    ["NETWORK", "MASK", "STARTADDR", "ENDADDR", "BROADCAST", "GATEWAY", "DNSSERVER"],
                    "/etc/dhcp/dhcpd.conf",
                    "a")

DHCP_ENABLE = Configurable('INTERFACES="%INT%"',
                           ["INT"],
                           "/etc/default/isc-dhcp-server",
                           "a")

INT_CONF = """
iface %INTERFACE% inet static
  address %IPADDR%
  netmask %MASK%
"""

INTERFACES = Configurable(INT_CONF,
                        ["INTERFACE","IPADDR","MASK"],
                        "/etc/network/interfaces",
                        "a")


HOSTAPD_CONF = """
interface=%INTERFACE%
# driver=rtl871xdrv (pi3)
ssid=%SSID%
country_code=US
hw_mode=g
channel=6
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=%PASS%
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
wpa_group_rekey=86400
ieee80211n=1
wme_enabled=1
"""

HOSTAPD = Configurable(HOSTAPD_CONF,
                       ["INTERFACE","SSID","PASS"],
                       "/etc/hostapd/hostapd.conf",
                       "w")

DEF_HOSTAPD = Configurable("DAEMON_CONF="+HOSTAPD.file+"\n",
                         [],
                         "/etc/default/hostapd",
                         "a")

INITD_HOSTAPD = Configurable("",
                             ["DAEMON_CONF="],
                             "/etc/init.d/hostapd",
                             "r")
INITD_HOSTAPD.set_attrs("DAEMON_CONF="+HOSTAPD.file)

SYSCTL = Configurable("net.ipv4.ip_forward=1 \n",
                      [],
                      "/etc/sysctl.conf",
                      "a")
