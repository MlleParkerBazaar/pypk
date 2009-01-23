#!/usr/bin/env python
# multiplesrc.py

"""Perform a lot of knocks quickly by spoofing src ip address."""

# should works on *nix systems only because Windows porting of
# pcapy appears to be still incomplete (2006-11-10).

from scapy import send, IP, TCP
import random

def knock(ip_src, ip_dst, d_port):
    # yeah, it's so easy
    send(IP(src=ip_src, dst=ip_dst)/TCP(flags='S', sport=666, dport=d_port))
    print "Knocked %s:%s" %(ip_src, d_port)

if __name__ == '__main__':
    src = ['10.0.0.5', '10.0.0.222']
    dst = '10.0.0.1'
    ports = [1,2,3,4,5,6]
    while 1:
        knock(random.choice(src), dst, random.choice(ports))
