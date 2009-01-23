#!/usr/bin/env python

########################################################################
#                                                                      #
# Date: 2006-02-01                                                     #
# Name: Py-Port Knocking project (pknockd.py)                          #
# Version - v0.1                                                       #
# Description - A port knock daemon Python implementation              #
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

### knockd.py

from   impacket import ImpactPacket
from   impacket.ImpactDecoder import *
from   decimal import Decimal
from   conf import Config
import threading
import pcapy
import time
import subprocess
import traceback
import sys



class Sniffer:
    """ Main class used to listen on the ethernet interface and sniff
incoming packets"""
    
    def __init__(self):
        pass

    def listen_int(self, dev):
        # Listens on given ethernet interface
        self.p = pcapy.open_live(dev, 1500, 0, 100)
        self.p.setfilter('tcp')
        print "Name: %s\nNet:  %s\nMask: %s\n" \
              %(dev, self.p.getnet(), self.p.getmask())
        Logger("Listening on: %s\n\n" %dev)
        (self.p.loop(-1, self.process_incoming_pkts))

    def process_incoming_pkts(self, hdr, data):
        # Decode received packets
        eth = EthDecoder().decode(data) # ETHernet frame
        ip = eth.child() # IP datagram
        tcp = ip.child() # TCP datagram
        self.ip_src = ip.get_ip_src()
        self.tcp_dport = tcp.get_th_dport()

        global active_seq, current_seq

        # Eseguito se e' stato incominciato uno knocking
        # (primo pacchetto della sequenza gia' stato mandato)

        if (active_seq == True) and (self.tcp_dport in SEQUENCES[current_seq]):
            t = Verifier(self.ip_src, self.tcp_dport).start()

        # Eseguito se non ci sono knocking in corso
        
        if (active_seq == False):
            for i in range(len(SEQUENCES)):
                if self.tcp_dport == SEQUENCES[i][0]:
                    active_seq  = 1
                    current_seq = i
                    t = Verifier(self.ip_src, self.tcp_dport).start()
                    p = Timer().start()


class Verifier(threading.Thread):
    """Verifies incoming sequences"""
    
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.ip   = ip
        self.port = port
        
    def run(self):
        global x, y, SEQUENCES, current_seq, active_seq

         ### Right knock ###
        if self.port == SEQUENCES[current_seq][x]:
            Logger("[%s] %s:%-3s %s OK!\n" %(time.strftime("%Y-%m-%d %H:%M:%S"),
                   self.ip, self.port, KNOCK_NAMES[int(current_seq)][0]), on_screen=True)
            self.lock.acquire()
            x += 1
            self.lock.release()
            
            ### Sequence completed ###
            if x == len(SEQUENCES[current_seq]):
                #print "Sequence OK"
                self.lock.acquire()
                knock_name = KNOCK_NAMES[current_seq][0]
                if "%IP%" in COMMANDS[current_seq][0]:
                    command = COMMANDS[current_seq][0].replace("%IP%", self.ip)
                else:
                    command = COMMANDS[current_seq][0]
                Logger("[%s] %s COMPLETE!\n" %(time.strftime("%Y-%m-%d %H:%M:%S"),
                       knock_name), on_screen=True)
                Logger("Running command: '%s'\n\n" %command, on_screen=True)
                try:
                    if sys.platform.startswith('win32'):
                        subprocess.Popen(command,stdout=0) 
                    else:
                        c = ''
                        subprocess.Popen(command.split(' '),stdout=0)
                except:
                    logfile = open(LOGFILE,'a+')
                    traceback.print_exc(file=logfile)
                    logfile.write('\n')
                    logfile.close()
                    print " ERR: The execution of command returned an error. See log file for more details."
                x = 0
                active_seq = 0 # killa il timer
                current_seq = None
                active_seq  = 0
                self.lock.release()

        ### Wrong knock ###
        else:
            self.lock.acquire()
            x = 0
            self.lock.release()
            Logger("[%s] %s:%-3s %s WRONG!\n" %(time.strftime("%Y-%m-%d %H:%M:%S"),
                   self.ip, self.port, KNOCK_NAMES[current_seq][0]), on_screen=True)
            #print x, "\n"


class Timer(threading.Thread):
    """Sequence timer"""
    def __init__(self):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
    
    def run(self):
        global x, active_seq
        t = TIMEOUT + 1
        #print "timer start"
        while active_seq == 1:
            t = Decimal(t) - Decimal('0.2')
            time.sleep(0.2)
            if t == 0:
                self.lock.acquire()
                x = 0
                active_seq = 0
                self.lock.release()
                #print "timer stop"                
                Logger("[%s] %s knock timeout\n\n" %(time.strftime("%Y-%m-%d %H:%M:%S"),
                       KNOCK_NAMES[current_seq][0]), on_screen=True)
                break
        self.lock.acquire()    
        x = 0
        active_seq = 0
        self.lock.release()

class Logger:
    """Write daemon's log file and print messages on screen"""
    def __init__(self, string, on_screen=False):
        global logfile
        logfile = open(LOGFILE,'a+')
        logfile.write(string)
        logfile.close()
        if on_screen == True: self.on_screen(string)

    def on_screen(self, string):
        print string[:-1]
        
    

if __name__ == '__main__':
    
    # bools
    active_seq  = False
    current_seq = None

    # pointer
    x = 0 

    # vars
    platform = sys.platform
    c = Config()
    TIMEOUT = c.timeout()
    LOGFILE = c.logfile()
    INTERFACES = c.interfaces()
    KNOCK_NAMES, SEQUENCES, COMMANDS = c.knock()

    # start
    Logger("\n### Starting knockd on: %s\n\n" %time.strftime("%Y-%m-%d %H:%M:%S"), on_screen=True)
    n = Sniffer()
    for i in INTERFACES:
        threading.Thread(target=n.listen_int, args=(i,)).start()

