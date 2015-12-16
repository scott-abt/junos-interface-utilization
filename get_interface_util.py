#!/usr/bin/env python

"""
Retrieves the percent of utilized access ports on a Juniper EX switch.

Specifically written for Python 2.6 because that's what I have. Get the % of utilized interfaces on the stack. Do not include feeds or other
non-access ports.
"""

from ConfigParser import ConfigParser
import getpass
from netmiko import ConnectHandler
import xmltodict
import re

class AccessInterfaceUtilization:
    
    """
    Object containing utilization stats of a switch
    switch_dict needs to be in netmiko device format.
    """

    def __init__(self, ini_file="default.ini", switch_dict={}):

        self.ini_file = ini_file
        self.switch_dict = switch_dict
        self.up_access_interfaces = 0
        self.up_lacp_member_interfaces = 0
        self.total_interfaces = 0
        self.percent_utilization = 0

        try:
            self.cfg = ConfigParser()
            self.cfg.readfp(open(self.ini_file))
        except IOError as ioe:
            print("Error opening " + self.ini_file + " {0}".format(ioe))

        if len(self.switch_dict.keys()) > 0:
            # Need to create better way to get config for portability. Multiple
            # devices with multiple default creds.
            self.switch_dict['username'] = self.cfg.get('DEFAULT', 'username')
            self.switch_dict['password'] = self.cfg.get('DEFAULT', 'password')
            self.op_rpc = str(
                    'show ethernet-switching interfaces detail | display xml')

            # Create the connection and get the xml
            self.conn = ConnectHandler(**self.switch_dict)
            self.xml_output = self.conn.send_command(self.op_rpc)
            if self.switch_dict['username'] == "root":
                print("User is root")
                self.clean_xml = str(self.xml_output).strip().partition("\n")[0]
            else:
                print("User is " + self.switch_dict['username'])
                self.clean_xml = str(self.xml_output).strip().partition("\n")[2]

            print(self.clean_xml)
            
            self.dict_of_xml = xmltodict.parse(self.clean_xml)
            for interface in self.dict_of_xml['rpc-reply']['switching-interface-information']['interface']:
                self.gige_re = re.compile('ge-.*')
                if (self.gige_re.match(interface['interface-name']) and
                        interface['interface-port-mode'] == "Access" and
                        interface['interface-state'] == "up"):
                    self.up_access_interfaces += 1
        else:
            print("Got no devices")
            self.device_list = {}

def main():
    """
    If running from the command line, you must provide the INI file
    in a form that ConfigParser understands. Minimal example:
    [DEFAULT]
    username: myusername
    password: mypassword
    """
    from SWITCH_LIST import the_list
    for each_switch in the_list:
        print("Trying " + each_switch['ip'])
        util = AccessInterfaceUtilization("mycreds.ini", each_switch)
        print(util.up_access_interfaces)

if __name__ == "__main__":
    main()
