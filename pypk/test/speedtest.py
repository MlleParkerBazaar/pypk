#!/usr/bin/env python
# speedtest.py

"""
Perform a lot of knocks quickly.
"""

# This test script has been indispensable to write a correct
# synchronization between threads in knockd.
# I've spent a lot of time believing that threads synchronization
# was correct by testing knockd manually (slowly, by using knocker.py)
# when it wasn't.
# It could also be used as stress-test utility.

import socket
import random
import time

def knock(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.0)
    try:
        s.connect((host, port))
    except:
        print "Knocked on %s:%s" %(host,port)

if __name__ == '__main__':
    host = '10.0.0.15'
    ports = [2000,2001,2002]
    while 1:
        knock(host, random.choice(ports))
        time.sleep(0.001)

