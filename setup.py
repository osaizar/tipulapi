#!/usr/bin/python

import os
import sys

from config_hostapd import main as config_hostapd
from config_bridge import main as config_bridge
from config_routing import main as config_routing

from commands import getoutput as run_command

def main():
    try:
        while True:
          cmd = raw_input("shell > ")
          run(cmd)
    except KeyboardInterrupt:
        end()

def run(cmd):
    if cmd in ["ip","ifconfig","ipconfig"]:
        print run_command("ifconfig")
    elif cmd == "config-wifi":
        if "y" in raw_input("enable wifi router mode? (y/n)"):
            config_hostapd()
    elif cmd == "config-routing":
        if "y" in raw_input("enable routing? (y/n)"):
            config_routing()
    elif cmd == "config-bridge":
        if "y" in raw_input("enable bridge? (y/n)"):
            config_bridge()
    elif "run" in cmd:
        cmd = cmd.split("run ")[1]
        print run_command(cmd)
    elif cmd == "exit":
        end()
    else:
        print "Ez da komandoa topatu"

def end():
    print "[+] Ayo!"
    sys.exit()

if __name__ == "__main__":
  main()
