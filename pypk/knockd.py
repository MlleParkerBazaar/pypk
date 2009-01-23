#!/usr/bin/env python
# knockd.py

"""
Py-port knocking project (daemon).
A port knock daemon that allows a remote client to open/close a certain
port(s) on the server by sending a prespecified sequences of TCP (SYN)
packets. 
"""

__pname__   = 'Py-port knock daemon'
__ver__     = 'v0.2'
__state__   = 'beta'
__date__    = '2006-11-25'
__author__  = 'billiejoex (ITA)'
__web__     = 'http://billiejoex.altervista.org'
__mail__    = 'billiejoex@gmail.com'
__license__ = 'see LICENSE.TXT'


import time
import traceback
import sys
import os
import copy
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
try:
    import threading
    import Queue
except ImportError:
    print "Your OS or Python interpreter does not support multi-threading."
    os._exit(0)
try:
    import subprocess
except ImportError:
    msg = "Your OS doesn't support sub-shell command execution.\n"
    msg+= "Compatible systems are Macintosh, UNIX(es) and Windows."
    print msg
    os._exit(0)    
try:
    import pcapy
except ImportError:
    print "pcapy module isn't installed."
    os._exit(0)

from  modules import configparser
from  modules import ImpactPacket
from  modules.ImpactDecoder import EthDecoder


def logger(string, withtime=True):
    """Log on screen and (optionally) on a file."""
    # TO DO - syslog logging.    
    if withtime:
        ctime = time.strftime("[%Y-%b-%d %H:%M:%S] ")
    else:
        ctime = ""
    print '%s%s' %(ctime, string)
    if LOGFILE:
        try:
            logfile = open(LOGFILE, 'a+')
            logfile.write('%s%s\n' %(ctime, string))
            logfile.close()
        except:
            globals()['LOGFILE'] = False
            logger("warning: file logging disabled.")
            f = StringIO.StringIO()
            traceback.print_exc(f)
            trace = f.getvalue()
            logger(trace, withtime=0)

                   
def exec_cmd(command, ip):
    """Executes a command once a sequence is satisfied."""
    if '%IP%' in command:
        command = command.replace('%IP%', ip)
    logger("Running command: '%s'" %command)
    if os.name not in ('nt', 'ce'):
        command = command.split(' ')
    try:
        subprocess.Popen(command, stdout=subprocess.PIPE)
    except:
        logger('Cmd execution returned an error:')        
        logger(str(sys.exc_value), withtime=0)
        
       
class core(threading.Thread):
    """Main class used to listen on ethernet interface and 
    filter/process incoming packets through libpcap."""
    
    def __init__(self, device):
        self.lt = local_table()
        self.rt = remote_table()
        self.kct = keep_count_table()
        self.dev = device
        threading.Thread.__init__(self)

    def run(self):
        pcap = pcapy.open_live(self.dev, 1500, 0, 100)
        pcap.setfilter('tcp')
        logger("name: %s\nnet:  %s\nmask: %s\n" %(self.dev, pcap.getnet(), pcap.getmask()), withtime=0)
        (pcap.loop(-1, self.process_incoming_pkts))

    def process_incoming_pkts(self, hdr, data):
        # decode received packets
        eth = EthDecoder().decode(data) 
        ip = eth.child()
        tcp = ip.child()
        ip_src = ip.get_ip_src()
        d_port = tcp.get_th_dport()
        
        # -- 3-way handshakes handling --
        #
        # discussion:
        # *SYN* flag of a TCP packet is usually activated during the first
        # and the second stage of a 3-way handshake process:
        #
        # A  ---SYN--->  B
        # A  <-SYN,ACK-  B
        # A  ---ACK--->  B
        #      
        # If a 3whs occurs and if TCP port is used inside a sequence,
        # we have to ignore the second TCP packet having ACK flag activated.
        
        if tcp.get_SYN:
            if not tcp.get_ACK():
                if d_port in self.lt.accepted_ports:
                    self.check_knock(ip_src, d_port)

    def check_knock(self, ip, port):
        # x.x.x.x --> sequence in progress
        global_lock.acquire()
        if self.rt.has_key(ip):
            knock_name= self.rt.get_knock_name(ip)
            full_seq  = self.lt.get_seq_from_knock_name(knock_name)
            satisfied_seq = self.rt.get_satisfied_seq(ip)
            pointer = len(satisfied_seq)

            # right knock
            if port == full_seq[pointer]:
                logger('%s %s:%s OK!' %(self.rt.get_knock_name(ip), ip, port))
                self.rt.append(ip, port)

                # sequence completed
                if full_seq == satisfied_seq:
                    knock_name = self.rt.get_knock_name(ip)
                    logger("%s %s COMPLETE!" %(knock_name, ip))

                    # remember seqs to repeat later                    
                    if knock_name in self.lt.seqs_to_count:
                        self.kct.append(knock_name, ip)

                    # execute cmd x times
                    if self.rt.get_keep_count(ip):
                        if self.kct.has_keys(self.rt.get_keep_count(ip), ip):                            
                            timer_obj = self.rt.get_timer_obj(ip)
                            timer_obj.stop()
                            for i in range(0, self.kct.get_times(self.rt.get_keep_count(ip), ip)):
                                exec_cmd(self.rt.get_cmd(ip), ip)
                            self.kct.delete(self.rt.get_keep_count(ip), ip)
                            self.rt.delete(ip)
                            global_lock.release()
                            return
                        else:
                            pass
                        
                    # execute cmd one time
                    timer_obj = self.rt.get_timer_obj(ip)
                    timer_obj.stop()
                    exec_cmd(self.rt.get_cmd(ip), ip)
                    self.rt.delete(ip)
                    global_lock.release()
                    return
                else:
                    global_lock.release()

            # wrong knock
            else:
                logger('%s %s:%s WRONG!' %(self.rt.get_knock_name(ip), ip, port))
                self.rt.reset_seq(ip)
                global_lock.release()
                return
            
        # x.x.x.x --> new sequence
        else:
            if port in self.lt.first_ports:
                self.rt.new(ip, port)
                logger('%s %s:%s OK!' %(self.rt.get_knock_name(ip), ip, port))
                global_lock.release()
                return
            global_lock.release()


class keep_count_table:
    """This class is an high-level interface to KEEP_COUNT_TABLE (dictionary).
    When "keep_count=<sequence>" option is used inside a sequence statement
    this class will "remember" how many times <sequence> is satisified.    
    
          |--name--|    |---ip---| |counter|
    
    x = {'[open SSH]': {'10.0.0.11': 3,
                        '10.0.0.20': 2},
         
         '[open xxx]': {'10.0.0.15': 1,
                        '10.0.0.66': 5}
         }
    """    

    def __init__(self):
        self.kct = KEEP_COUNT_TABLE

    def append(self, knock_name, ip):
        if not self.kct.has_key(knock_name):
            self.kct[knock_name] = {ip : 1}
        else:
            if ip not in self.kct[knock_name]:
                self.kct[knock_name][ip] = 1
            else:
                self.kct[knock_name][ip] = self.kct[knock_name][ip] + 1

    def get_times(self, knock_name, ip):
        return self.kct[knock_name][ip]

    def delete(self, knock_name, ip):
        del(self.kct[knock_name][ip])

    def has_keys(self, knock_name, ip):
        if self.kct.has_key(knock_name):
            if self.kct[knock_name].has_key(ip):
                return 1
        return 0
                     
    
class local_table:
    """This class is an high-level interface to LOCAL_TABLE object, 
    a dictionary containing all knock-sequences specified in
    knockd.conf. 
    
    LOCAL_TABLE = {'[open SSH]':  {'command': 'cmd 1',
                                   'sequence': [2000, 2001, 2002],
                                    keep_count': None},
                                  
                   '[close SSH]': {'command': 'cmd 2',
                                   'sequence': [4000, 4001, 4002],
                                   'keep_count': '[open SSH]'}}     
    """
    
    def __init__(self):                         
        self.lt = LOCAL_TABLE
        self.accepted_ports = self.__get_accepted_ports()        
        self.first_ports = self.__get_all_first_ports()
        self.seqs_to_count = self.__get_seqs_to_count()

    def get_rt_obj_from_first_port(self, port):
        seq_name = self.__get_seqname_from_first_port(port)
        params = self.lt[seq_name]        
        return (seq_name, copy.copy(params))

    def get_seq_from_knock_name(self, name):
        return self.lt[name]['sequence']

    # privates:
    
    def __get_accepted_ports(self):
        ports = []
        for seq in self.lt:
            for port in self.lt[seq]['sequence']:
                ports.append(port)
        return ports

    def __get_all_first_ports(self):
        ports = []
        for seq in self.lt:
            ports.append(self.lt[seq]['sequence'][0])
        return ports

    def __get_seqname_from_first_port(self, port):
        for seq in self.lt:
            if self.lt[seq]['sequence'][0] == port:
                return seq

    def __get_seqs_to_count(self):
        l = []
        for seq in self.lt:
            if self.lt[seq]['keep_count'] != None:
                l.append(self.lt[seq]['keep_count'])
        return l
            
      
class remote_table:
    """
    This class is used as high-level interface to REMOTE_TABLE object, 
    a dictionary containing all pending knock-sequences. Every key of the
    dictionary contains:
    - the ip_src address of the knocker (dictionary's key).
    - the current sequence satisfied by the knocker.
    - the command to execute if the sequence is satisfied.
    - a shared timer object used by "Timer" class in case that the sequence
      doesn't take place within the time expected (timeout occurred).

        { 10.0.0.1': {'name' : 'Open SSH'
                      'command': 'cmd 1',
                      'sequence': [2000],
                      'keep_count': None,
                      'timer_obj' : obj},
         ...
        }              
    """
    
    def __init__(self):
        self.rt = REMOTE_TABLE

    def has_key(self, key):
        if self.rt.has_key(key):
            return 1
        return 0
            
    def new(self, ip, port):
        """Create a new remote_table object:

        {...
         ...
         '10.0.0.1': {'name' : 'Open SSH'
                      'command': 'cmd 1',
                      'sequence': [2000],
                      'keep_count': None,
                      'timer_obj' : obj},
         ...
         ...
        }        
        """
        seq_name, params = local_table().get_rt_obj_from_first_port(port)
        params['name'] = seq_name
        params['sequence'] = [port]
        timer_obj = Timer(ip, self)
        timer_obj.start()
        params['timer_obj'] = timer_obj        
        self.rt[ip] = params
        return 1
    
    def append(self, ip, port):
        """Append a new seq number to knocker's key."""
        self.rt[ip]['sequence'].append(port)
 
    def delete(self, ip):
        """Delete knocker."""
        del self.rt[ip]

    def reset_seq(self, ip):
        """Flush knocker's satisfied sequence."""
        self.rt[ip]['sequence'] = []

    # Get params from %IP%
    
    def get_knock_name(self, ip):
        return self.rt[ip]['name']

    def get_satisfied_seq(self, ip):
        return self.rt[ip]['sequence']

    def get_cmd(self, ip):
        return self.rt[ip]['command']

    def get_keep_count(self, ip):
        return self.rt[ip]['keep_count']      

    def get_timer_obj(self, ip):
        return self.rt[ip]['timer_obj']

        
class Timer:
    """A timer started every time a new sequence starts.
    If the knocker doesn't complete the sequence within TIMEOUT
    value its entry will be deleted from remote_table."""

    def __init__(self, ip, rt_instance):
        self.ip = ip
        self.rt_instance = rt_instance
        self.timer = threading.Timer(TIMEOUT, self.timeout)          

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def timeout(self):
        global_lock.acquire()
        if self.rt_instance.has_key(self.ip):
            logger("%s %s knock timeout" % (self.rt_instance.get_knock_name(self.ip), self.ip))
            self.rt_instance.delete(self.ip)
        global_lock.release()
        

def run():
    global LOGFILE, TIMEOUT, LOCAL_TABLE, REMOTE_TABLE, \
           KEEP_COUNT_TABLE, global_lock
       
    # helper
    helper = """\n\
NAME:
  Py-port knock daemon %s

DESCRIPTION:
  A port knock daemon that allows a remote client to open/close a certain
  port(s) on the server by sending a prespecified sequences of TCP (SYN)
  packets. 

USAGE:
  %s [conf_file]""" %(__ver__, os.path.split(sys.argv[0])[1])
    
    # cmd line parser
    conffile = None
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', '/?']:
            print helper
            os._exit(0)
        else:
            conffile = sys.argv[1]            
    try:
        conf = configparser.parse(conffile)
    except configparser.Error, err:
        print err
        os._exit(0)
    
    # collecting main vars
    LOGFILE = conf.get_logfile()
    TIMEOUT = conf.get_timeout()
    LOCAL_TABLE = conf.get_sequences()
    REMOTE_TABLE = {}
    KEEP_COUNT_TABLE = {}
    devices = conf.get_interface()
    no_devs = len([dev for dev in pcapy.findalldevs() \
                   if dev not in ('any', '\Device\NPF_GenericDialupAdapter')])

    # create a global lock object needed for threads synchronization.
    global_lock = threading.Lock()
    
    # starting msg
    msg = "%s %s\n" %(__pname__, __ver__)
    msg+= "Started at: %s\n" %time.strftime("%Y-%b-%d %H:%M:%S")
    msg+= "Total available interfaces: %s\n" %no_devs
    msg+= "Listening on:\n"
    logger(msg, withtime=0)

    # start serve
    for dev in devices:
        core(dev).start()

if __name__ == '__main__':
    # check if other pknockd instances are currently running on the system.
    # TO DO - win NT service support.
    # TO DO - daemonize on unix. 
    if os.name in ['nt', 'ce']:       
        try:
            from win32event import CreateMutex
            from win32api import GetLastError
            from winerror import ERROR_ALREADY_EXISTS
            handle = CreateMutex(None, 1, 'py-port-knock-daemon')
            if GetLastError() == ERROR_ALREADY_EXISTS:
                msg = 'Another instance of knockd is already running.'
                print msg
                import win32ui, win32con        
                win32ui.MessageBox(msg, sys.argv[0], win32con.MB_ICONERROR)
                os._exit(0)
            else:
                # this is the only instance of the script, let
                # it do its normal work.
                pass
        except ImportError:
            print "warning: pywin32 extension isn't installed."
            print "knockd will run anyway."
            pass
    run()
