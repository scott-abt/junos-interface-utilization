#!/usr/bin/env python

"""
Specifically written for Python 2.6 because that's what I have.

Get the % of utilized interfaces on the stack. Do not include feeds or other
non-access ports.
"""

# RPC calls can be returned in XML format in Junos by passing "| display xml"
# to the command. Can I use the json module to parse the XML to a dict?

from ConfigParser import ConfigParser
import getpass
from netmiko import ConnectHandler

class AccessInterfaceUtilization:
    
    """
    Object containing utilization stats of a switch
    device_dict needs to be in netmiko device format.
    """

    def __init__(self, ini_file="default.ini", device_dict={}):
        # create connection to juniper device and get the output from "show
        # interfaces terse | display xml"

        try:
            cfg = ConfigParser()
            cfg.readfp(open(ini_file))
        except IOError as ioe:
            print("Error opening " + ini_file + " {0}".format(ioe))

        if len(device_dict.keys()) > 0:
            print(len(device_dict.keys()))

            device_dict['username'] = cfg.get('DEFAULT', 'username')
            self.op_rpc = "show interfaces terse | display xml"
        else:
            print("Got no devices")

def main():
    from SWITCH_LIST import the_list
    for each_switch in the_list:
        print("Trying " + each_switch['ip'])
        util = AccessInterfaceUtilization("mycreds.ini", )

if __name__ == "__main__":
    main()
