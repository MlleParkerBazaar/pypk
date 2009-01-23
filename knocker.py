#!/usr/bin/env python

########################################################################
#                                                                      #
# Date: 2006-02-01                                                     #
# Name: Py-Port Knocking project (knocker.py)                          #
# Version: v0.1                                                        #
# Description: A simple port knock client that sends TCP (SYN)         #
#   packets on prespecified ports                                      #
# Author: billiejoex                                                   #
# License: GNU                                                         #
# Web: http://billiejoex.altervista.org                                #
#                                                                      #   
# Knockd project is a free software; you can redistribute it and or    #
# modify it under the terms of the GNU General Public License as       #
# published by the Free Software Foundation; either version 2 of the   #
# License, or (at your option) any later version.                      #
# Soicmp is distributed in the hope that it will be useful,            #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# For further informations please visit:                               #
# http://billiejoex.altervista.org/Prj_Py-port_knock.htm               #
#                                                                      #
########################################################################

### knocker.py

import socket
import sys
import os
import getopt
import time

def knock(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.0)
    try:
        s.connect((host, port))
    except:
        print "Knocked on %s:%s" %(host,port)
        pass

def parser():
    global host, ports
    ports = []
    try: opts, args = getopt.getopt(sys.argv[1:], "")
    except: helper(); os._exit(0)
    if len(args) < 2: helper(); os._exit(0)
    host = args[0]
    p = args[1].split(',')
    for port in p:
        ports.append(port)
        
def helper():
    print """\
TCP port knocker client - by: billiejoex

Syntax:
  %s <remote_host> [port|port,port]
 
Examples:
  python %s 10.0.0.1 2000
  python %s 10.0.0.1 2000,2100,2200
""" %(sys.argv[0],sys.argv[0],sys.argv[0])

if __name__ == '__main__':
    parser()  
    try: ip = socket.gethostbyname(host)
    except: print "Unknown address"; os._exit(0)
    for i in ports:
        knock(host,int(i))
        time.sleep(0.3)
