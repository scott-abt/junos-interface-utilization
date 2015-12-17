#!/usr/bin/env python

"""
Retrieves the percent of utilized access ports on a Juniper EX switch.

Specifically written for Python 2.6 because that's what I have. Get the % of utilized interfaces on the stack. Do not include feeds or other
non-access ports.
"""

import getpass, sys, xmltodict, re
from netmiko import ConnectHandler
from argparse import ArgumentParser as AP
from argparse import FileType
from ConfigParser import ConfigParser

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
            self.op_rpc = str(
                    'show ethernet-switching interfaces detail | display xml')

            # Create the connection and get the xml
            self.conn = ConnectHandler(**self.switch_dict)
            self.xml_output = self.conn.send_command(self.op_rpc)

            if self.switch_dict['username'] == "root":
                self.clean_xml = str(self.xml_output).partition("\n")[2]
            else:
                self.clean_xml = str(self.xml_output).strip().partition("\n")[2]
            
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
    arg_parser = AP()
    
    arg_parser.add_argument('username',
            help='Switch user with operator priveleges')
    arg_parser.add_argument('-p', dest='password',
            action='store_true',
            default=False,
            help='Configure the switch password')
    arg_parser.add_argument('cfg_file', 
            default="SWITCH_LIST",
            help="Imports list of dicts from a local file. default is "
            "SWITCH_LIST.py")
    result = arg_parser.parse_args()

    if result.password:
        switch_pass = getpass.getpass()
    else:
        switch_pass = ""
    
    SWITCH_LIST = __import__(result.cfg_file)
    for switch_dict in SWITCH_LIST.the_list:
        switch_dict['username'] = result.username
        switch_dict['password'] = switch_pass
        arp_table = AccessInterfaceUtilization("mycreds.ini", switch_dict)
        print(arp_table.up_access_interfaces)

if __name__ == "__main__":
    main()
