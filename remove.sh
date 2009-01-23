#!/bin/sh

### debug script
set -x

rm /usr/sbin/knockd
rm /usr/sbin/knocker
rm /etc/knockd.conf
rm /usr/share/man/man8/knockd.8.gz
rm -Rf /usr/lib/python2.4/site-packages/ppknock

