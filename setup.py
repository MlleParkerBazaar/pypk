#!/usr/bin/env python

"""pypk installer script. Use it to install pypk
under UNIX like systems."""

import os
from distutils.core import setup
import glob
try:
    import pcapy
except ImportError:
    print "Install pcapy extension first."
    os._exit(0)
    

if os.name in ['nt', 'ce']:
    print "This script is for *nix systems only."
    os._exit(0)


setup(name='Py-port knocking',
      version="v0.2",       
      author='billiejoex',
      author_email='billiejoex@gmail.com',
      maintainer='billiejoex',
      maintainer_email='billiejoex@gmail.com',
      url='http://billiejoex.altervista.org',
      description='A python port knocking system implementation.',
      long_description='Read doc/Py-port-knocking-project.html',
      classifiers=[
          'Development Status :: Beta',
          'Environment :: Console',
          'Intended Audience :: System Administrators :: Paranoids',
          'License :: GNU',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          ],
      
      packages=[
          'pypk',
          'pypk/modules',
          'pypk/test'],
      
      package_data={
          'pypk/test': ['*.conf']
          },
      
      data_files=[
          ('sbin', ['pypk/posix/knockd']),
          ('sbin', ['pypk/posix/knocker']),
          ('/usr/share/man/man8', ['pypk/posix/man/knockd.8.gz']),
          ('/etc/', ['pypk/knockd.conf'])
          ]
      )

os.system('chmod +x /usr/sbin/knockd')
os.system('chmod +x /usr/sbin/knocker')

