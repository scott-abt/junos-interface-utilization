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
    switch_dict needs to be in netmiko device format.
    """

    def __init__(self, ini_file="default.ini", switch_dict={}):
        # create connection to juniper device and get the output from "show
        # interfaces terse | display xml"

        self.ini_file = ini_file
        self.switch_dict = switch_dict
        try:
            self.cfg = ConfigParser()
            self.cfg.readfp(open(self.ini_file))
        except IOError as ioe:
            print("Error opening " + self.ini_file + " {0}".format(ioe))

        if len(self.switch_dict.keys()) > 0:
            # Initialize the connection variables.
            self.switch_dict['username'] = self.cfg.get('DEFAULT', 'username')
            self.switch_dict['password'] = self.cfg.get('DEFAULT', 'password')
            self.op_rpc = "show ethernet-switching interfaces detail | display xml"

            # Create the connection and get the xml
            self.conn = ConnectHandler(**self.switch_dict)
            self.xml_output = self.conn.send_command(self.op_rpc)
            print(self.xml_output)

            # Parse the XML for the active, access interfaces (not xe-* or
            # tagged interfaces)
            # Question of the day: How do I do that?

        else:
            print("Got no devices")

def main():
    """
    If running from the command line, you must provide the file 'mycreds.ini'
    in a form that ConfigParser understands. Minimal example:
    [DEFAULT]
    username: myusername
    password: mypassword
    """
    from SWITCH_LIST import the_list
    for each_switch in the_list:
        print("Trying " + each_switch['ip'])
        util = AccessInterfaceUtilization("mycreds.ini", each_switch)

if __name__ == "__main__":
    main()
