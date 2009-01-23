
### conf.py

"""An extension class used by knockd.py daemon"""

import os 
import pcapy

class Config:
    """Parse directives in knockd.conf"""
    def __init__(self):
        self.TIMEOUT = None
        self.LOGFILE = None
        self.INTERFACES = []
        self.KNOCK_NAMES = []
        self.SEQUENCES = []
        self.COMMANDS  = []
        
        self.f = open("knockd.conf","r+")
        self.l = self.f.readlines()
        self.list = []
        
        # Ignore '\n' e '#'    
        x = -1
        for i in self.l:
            x += 1
            if not i.startswith("#"):
                if not i.startswith("\n"):
                    self.list.append(i.replace('\n',''))

    def timeout(self):
    ### get TIMEOUT var
        for i in self.list:
            if i.startswith("timeout="):
                self.TIMEOUT = i.split('=')[1]
        if self.TIMEOUT == None:
            print "You have to specify 'timeout' directive in knockd.conf"
            os._exit(0)
        return int(self.TIMEOUT)

    def logfile(self):
    ### get LOGFILE var
        for i in self.list:
            if i.startswith("logfile="):
                self.LOGFILE = i.split('=')[1]
        if self.LOGFILE == None:
            print "You have to specify 'logfile' directive in knockd.conf"
            os._exit(0)
        return self.LOGFILE

    def interfaces(self):
    ### get INTERFACES var
        try:
            self.devs = []
            for i in pcapy.findalldevs():
                if i not in ('any', '\Device\NPF_GenericDialupAdapter'):
                    self.devs.append(i)
        except:
            print " ERR: No valid ethernet interfaces to open.\n \
                  Are you sure you have right priviledges?", os._exit(0)



            
        int = []
        for i in self.list:
            if i.startswith("interface="):
                int.append(i[10:])
                
        if int == ['']:
            print " ERR: No interfaces specified in knockd.conf file"
            print " Choose one of the following interfaces and edit your knockd.conf file: \n"
            self.show_all_int()
            os._exit(0)

        if int[0] == "ALL":
            for i in self.devs:
                self.INTERFACES.append(i)
            
        if self.INTERFACES == []:
            for i in int:
                if i in self.devs:
                    self.INTERFACES = int
                    pass
                else:
                    print "\n ERR: Unknown interface '%s'\n Choose one of the followings:\n" %i
                    self.show_all_int()
                    self.choose_interface(self.devs, i)
                    
        return self.INTERFACES

    def show_all_int(self):
        """"return and print a list of all ethernet interfaces avaible"""
        self.devs = pcapy.findalldevs()
        x = 0
        for i in self.devs:
            self.p = pcapy.open_live(i, 1500, 0, 100)
            print " Device number: [%s]\n Name: %s\n Net : %s\n Mask: %s\n" %(x, i, self.p.getnet(), self.p.getmask())
            x += 1
        return self.devs
        

    def choose_interface(self, devs, err):
    ### fix a bad INTERFACE value by directly modifying knockd.conf file
        self.devs.append('ALL')
        print " Device number: [%s] \n Name: ALL (listens on all int)\n Net : *.*\n Mask: *.*\n" %(len(devs) -1)
        while 1:
            try:
                c = input('Put device number here: ')
            except:
                print " ERR Insert an integer value"
                continue
            if (c > len(devs)-1):
                print " ERR Too high! Insert a value from 0 to %s" %(len(devs) -1)
            elif (c < 0):
                print " ERR Too low! Insert a value from 0 to %s" %(len(devs) -1)
            else:
                break
        f = open('knockd.conf','r')
        text = f.read()
        f.close
        f = open('knockd.conf','w')
        f.write(text.replace(err, devs[c]))
        f.close()
        print "knockd.conf modified. Restart knockd."
        os._exit(0)

    def knock(self):
    ### get KNOCK_NAMES, SEQUENCES, COMMANDS vars
        x = -1
        la = []
        lb = []
        for i in self.list:
            x += 1
            if i.find('[') >= 0:
                la.append(x)
        la.append(len(self.list))
        x = 0
        y = 2
        for i in la:
            lb.append(la[x:y])
            x += 1
            y += 1
        lb.remove(lb[len(lb)-1])
        directive = ''
        s = []
        for i in lb:
            directive = self.list[i[0]:i[1]]
            for i in directive:
                x = []
                if i.startswith('['):
                    x = [i]
                    self.KNOCK_NAMES.append(x)

                x = []    
                if i.startswith("sequence="):
                     y = i[9:].split(',')
                     for elem in y:
                         x.append(int(elem))
                     self.SEQUENCES.append(x)
                    
                x = []
                if i.startswith("command="):
                    x = [i[8:]]
                    self.COMMANDS.append(x)

        ### missing controls
        if self.KNOCK_NAMES == []:
            print " ERR: You have to specify at least one [Sequence Name] directive in knockd.conf"
            os._exit(0)
        if self.SEQUENCES == []:
            print " ERR: You have to specify at least one sequence in knockd.conf"
            os._exit(0)
        if self.COMMANDS == []:
            print " ERR: You have to specify at least one command in knockd.conf"
            os._exit(0)
            
        ### are there some seq starting with the same port num?
        for i in self.SEQUENCES:
            y = i[0]
            x = 0
            for f in self.SEQUENCES:
                if y == f[0]:
                    x += 1
                if x > 1:
                    print " ERR: Two sequences starts with the same port number."
                    os._exit(0)

        return self.KNOCK_NAMES, self.SEQUENCES, self.COMMANDS

