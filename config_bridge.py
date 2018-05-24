#!/usr/bin/python

# This script configurates a bridge between two ports
import os
import sys
from functions import *

def main():
    if not check_root():
        print "[!] You must run this script as root!"
        sys.exit(1)

    install_apt_dependencies('bridge')
    configure_bridge()

    print "[+] Done!"

if __name__ == "__main__":
    main()
