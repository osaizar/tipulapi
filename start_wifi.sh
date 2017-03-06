#!/bin/bash
service isc-dhcp-server restart
/usr/sbin/hostapd /etc/hostapd/hostapd.conf
