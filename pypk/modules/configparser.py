# configparser.py (the boring work)

"""knockd.conf parser."""

import os
import pcapy

class Error(Exception):
    """Base class for ConfigParser exceptions."""
    
    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message


class parse:

    def __init__(self, filename=None):
        self.main_entries = {}
        self.seqs = {}
        main_values = ['interface', 'logfile', 'syslog', 'timeout']
        seq_values = ['sequence', 'command', 'keep_count']
        ignore=['#','\n']        
        current_seq = None        
        lineno = 0	
        if filename == None:
            if os.name in ['nt','ce']:
                filename = 'knockd.conf'
            else:
                filename = '/etc/knockd.conf'
        try:
            file_obj = open(filename, 'r')
        except IOError, err:
            raise Error, err
        #
        # start parsing
        #
        while 1:
            # cleanup
            line = file_obj.readline()
            lineno += 1
            if not line:
                break
            line = line.strip()
            if line == '' or line[0] in ignore:
                continue

            # get sequence names
            if (line.startswith('[')) and (line.endswith(']')):
                current_seq = line
                self.seqs[line] = {}
                for entry in seq_values:
                    self.seqs[current_seq][entry] = None

            # get main entries
            elif (line.split('=')[0] in main_values):
                entry = line.split('=')[0]
                arg = line.split('=')[1]
                self.main_entries[entry] = arg

            # get sequences entries
            elif (line.split('=')[0] in seq_values):
                if current_seq:
                    entry = line.split('=')[0]
                    arg = line[len(entry) + 1:]
                    self.seqs[current_seq][entry] = arg
                else:
                    msg = 'statement:"%s", file:"%s", line:%s.\n' %(line, filename, lineno)
                    msg+= "No sequence associated with the given statement."
                    raise Error, msg
            else:
                raise Error, 'Unknwon value "%s" found in "%s", line %s.' %(line, filename, lineno)
        # ------------------------------------------------------------------------------------------

        # check main entries:

        # ethernet interfaces
        try:
            devs = [dev for dev in pcapy.findalldevs() if dev not in ('any', '\Device\NPF_GenericDialupAdapter')]
            for dev in devs:
                pcapy.open_live(dev, 1500, 0, 100)
        except pcapy.PcapError, err:
            msg = str(err)
            msg+="\nDo you have enough priviledges?"
            raise Error, msg   
        if not self.main_entries.has_key('interface') or not self.main_entries['interface']:
            raise Error, "No interfaces specified in %s." %filename
        else:
            if self.main_entries['interface'].lower() == 'all':
                self.main_entries['interface'] = devs
            else:
                if self.main_entries['interface'] in devs:
                    self.main_entries['interface'] = [self.main_entries['interface']]
                else:
                    msg = 'Unknown interface name "%s". ' %self.main_entries['interface']
                    msg+= 'Choose one of the followings:\n'
                    for dev in devs:
                        pcap = pcapy.open_live(dev, 1500, 0, 100)
                        msg+= "\nname: %s\nnet:  %s\nmask: %s\n" %(dev, pcap.getnet(), pcap.getmask())
                    raise Error, msg

        # logfile
        if not self.main_entries.has_key('logfile'):
            self.main_entries['logfile'] = False

##        # syslog
##        if self.main_entries.has_key('syslog'):
##            arg = self.main_entries['syslog'].lower().replace(' ','')
##            if arg == 'yes':
##                if os.name in 'posix':
##                    self.main_entries['syslog'] = True
##            elif arg == 'no':
##                self.main_entries['syslog'] = False
##            else:
##                msg = 'Error in %s, statement "sysylog=%s."' %(filename, self.main_entries['syslog'])
##                raise Error, msg
##        else:
##            self.main_entries['syslog'] = False

        # timeout
        if not self.main_entries.has_key('timeout') or not self.main_entries['timeout']:
            raise Error, "No sequence timeout specified in %s." %filename
        else:
            try:
                self.main_entries['timeout'] = int(self.main_entries['timeout'])
            except ValueError:
                raise Error, '"timeout" statement requires integer.'

        # check sequences entries
        first_ports = []        
        for seq_name in self.seqs:
            if not self.seqs[seq_name]['command'] or not self.seqs[seq_name]['command']:
                raise Error, "No command specified for sequence %s." %seq_name

            if not self.seqs[seq_name]['sequence'] or not self.seqs[seq_name]['sequence']:
                raise Error, "No port sequence specified for sequence %s." %seq_name

            if self.seqs[seq_name]['keep_count']:
                if self.seqs[seq_name]['keep_count'] == seq_name: 
                    raise Error, "keep_count argument can't be equal to knock name %s." %seq_name                
                if not self.seqs.has_key(self.seqs[seq_name]['keep_count']):
                    raise Error, 'Unknown sequence name used as "keep_count" argument in %s sequence.' \
                                  %seq_name

	    # turn sequence arg into a list and check if args are integers
            try:
                self.seqs[seq_name]['sequence'] = [int(i) for i in self.seqs[seq_name]['sequence'].split(',')]
                for port in self.seqs[seq_name]['sequence']:
                    if port > 65535:
                        raise Error, 'Specified port number value is too high (max: 65535): "sequence=%s".' %self.seqs[seq_name]['sequence']
                    if port < 1:
                        raise Error, 'Specified port number value is too low (min: 1): "sequence=%s".' %self.seqs[seq_name]['sequence']
                    if port not in first_ports:
                        first_ports.append(port)
                    else:
                        raise Error, 'Two sequences begin with the same port number value.'
            except ValueError:
                raise Error, 'Ports of sequence %s must be integers.' %seq_name

            if len(self.seqs[seq_name]['sequence']) < 2:
                raise Error, 'You have to specify at least 2 ports in %s sequence.' %seq_name


    def get_interface(self):
        return self.main_entries['interface']

    def get_logfile(self):
        return self.main_entries['logfile']

    def get_timeout(self):
        return self.main_entries['timeout']

    def get_syslog(self):
        return self.main_entries['syslog']

    def get_sequences(self):
        return self.seqs


