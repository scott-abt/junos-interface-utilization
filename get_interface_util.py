#!/usr/bin/env python

from jnpr.junos import Device
from jnpr.junos.exception import (
        ConnectError, ProbeError, ConnectAuthError, ConnectRefusedError, 
        ConnectTimeoutError)

import ConfigParser
from getpass import getpass

config = ConfigParser.ConfigParser()
config.read('default.ini')

u = raw_input("Username: ")
p = getpass()

if not u or u is "" or not p or p is "":
    print("Username or password not supplied, using defaults...")
    u = config.get('DEFAULT', 'username')
    p = config.get('DEFAULT', 'password')

Device.auto_probe = 10

sandbox = Device(host="10.56.133.100", user=u, password=p)

try:
    devOpenHandle = sandbox.open()
    # Get number of access interfaces
    # I think this can be done simply by grabbing all the ge-* interfaces and
    # excepting anything that's tagged. Need to make sure that interfaces that
    # are not configured are counted. Might have to do this simply with model
    # numbers since they don't seem to show up in either ethport or phyport
    # tables.

    # Determine % utilization - divide active interfaces by available
    # interfaces.
    # Spit out the number * 100

except ConnectAuthError as authe:
    print "Authentication failed: {0}".format(authe)
    # Try to get their credentials again
except ProbeError as pe:
    print "There was an error probing for NETCONF: {0}".format(pe)
    # log this
except ConnectRefusedError as cr:
    print "Connection was refused: {0}".format(cr)
except ConnectTimeoutError as ct:
    print "Connection timed out: {0}".format(ct)

