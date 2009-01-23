#!/usr/bin/env/python
# configparser.py

"""
Test configparser class by using knockd.py with
different types of incorrect configuration files.
"""

import os
import sys
import subprocess

def _clear():
    if os.name in ['nt', 'ce']:
        os.system('cls')
    else:
        os.system('clear')

def _quote(args):
    if args[0] == '':
        return ''
    else:
        s = ''
        if type(args) == type(()):
            for elem in args:            
                s += '"%s"' %elem
            return s[:-1]
        s = ''
        if type(args) == type(''):
            s += '"%s"' %args
            return s

def call(cmd, fileconf, comment):
    _clear()
    if os.name in ('nt', 'ce'):
        py = _quote(python) 
        prg = _quote(os.path.join(os.getcwd(), cmd))
        string = py + ' ' + prg + ' ' + fileconf
        print ">>> %s %s   # %s" %(cmd, fileconf, comment)
        try:
            subprocess.call(string, shell=False)
            a = raw_input()
        except KeyboardInterrupt:
            pass
    else:
        try:
            print ">>> %s %s   # %s" %(cmd, fileconf, comment)
            subprocess.call([python, cmd, fileconf])
            a = raw_input()
        except KeyboardInterrupt:
            pass

def run():
    f = 'knockd.py'
    call(f, 'test/01.conf', 'missing interface')
    call(f, 'test/02.conf', 'missing timeout')
    call(f, 'test/03.conf', "missing seq's seq")
    call(f, 'test/04.conf', "missing seq's cmd")
    call(f, 'test/05.conf', "timeout == type(str)")
    call(f, 'test/06.conf', "bad keep_count arg")
    call(f, 'test/07.conf', "keep_count == [current seq]")
    call(f, 'test/08.conf', "bad interface")
    call(f, 'test/09.conf', "port_seq == type(str)")
    call(f, 'test/10.conf', "len(port_seq) == 1")
    call(f, 'test/11.conf', "port_seq[x] > 65535")
    call(f, 'test/12.conf', "port seq[x] < 1")
    call(f, 'test/13.conf', "seq1[0] == seq2[0]")
    call(f, 'test/xx.conf', "invalid conffile name")

if __name__ == '__main__':
    os.chdir('..') 
    pyver = sys.version[0:3]
    if os.name in ('nt', 'ce'):
        python = r"%s\Python%s\python.exe" %(os.environ['SYSTEMDRIVE'], pyver.replace('.',''))
    else:
        python = "/usr/bin/python"
    if not os.path.exists(python):
        print "Can't find python interpreter."
        sys.exit()
    run()
    
