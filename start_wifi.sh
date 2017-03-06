#!/bin/bash
ifdown wlan0
ifconfig wlan0 192.168.55.1 
service isc-dhcp-server restart
/usr/sbin/hostapd /etc/hostapd/hostapd.conf
