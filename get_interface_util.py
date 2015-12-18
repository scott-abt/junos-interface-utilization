#!/usr/bin/env python

"""
Retrieves the number of utilized access ports on a Juniper EX switch.

Specifically written for Python 2.6 because that's what I have. Get the number
of utilized interfaces on the stack. Do not include feeds or other non-access ports.
"""

import xmltodict, re
from netmiko import ConnectHandler
from argparse import ArgumentParser as AP
import ConfigParser

class AccessInterfaceUtilization:
    
    """
    Currently only counts ge-* interfaces in an 'up' state.
    Does not count 'tagged' interfaces.
    """

    def __init__(self, ip_addr, cfg_file='default.ini'):

        self.ip_addr = ip_addr
        self.switch_dict = {
                'device_type': 'juniper',
                'ip': self.ip_addr,
                'username': '',
                'password': '',
            }

        self.cfg_file = cfg_file
        self.cfg_parser = ConfigParser.ConfigParser()
        try:
            self.result = self.cfg_parser.readfp(open(self.cfg_file))
        except IOError as ioe:
            print("Could not open " + self.cfg_file + ": {0}".format(ioe))
            throw

        # Cycle through the credentials given until we find one that works or
        # throw an error.
        self.count = 0
        for section in self.cfg_parser.sections():
            user = self.cfg_parser.get(section, 'username')
            password = self.cfg_parser.get(section, 'password')
            self.switch_dict['username'] = user
            self.switch_dict['password'] = password
            
            try:
                self.conn = ConnectHandler(**self.switch_dict)
            except Exception as e:
                print("Could not connect: {0}".format(e))
                if self.count <= len(self.cfg_parser.sections()):
                    self.count += 1
                    pass
                else:
                    raise
            pass

        self.op_rpc = (
                'show ethernet-switching interfaces detail | display xml')
        self.xml_output = self.conn.send_command(self.op_rpc)

        if self.switch_dict['username'] == "root":
            self.clean_xml = str(self.xml_output).partition("\n")[2]
        else:
            self.clean_xml = str(self.xml_output).strip().partition("\n")[2]

        self.dict_of_xml = xmltodict.parse(self.clean_xml)
        self.up_access_interfaces = 0
        for interface in self.dict_of_xml['rpc-reply']['switching-interface-information']['interface']:
            self.gige_re = re.compile('ge-.*')
            if (self.gige_re.match(interface['interface-name']) and
                    interface['interface-port-mode'] == "Access" and
                    interface['interface-state'] == "up"):
                self.up_access_interfaces += 1

def main():

    cfg_file="default.ini"
    arg_parser = AP()
    arg_parser.add_argument('-i', dest='ip_addr',
            help="IP address or FQDN of the switch")
    arg_parser.add_argument('-c,', dest='cfg_file',
            help="INI file containing credentials. See default.ini for"
                " example")

    result = arg_parser.parse_args()
    if result.cfg_file:
        cfg_file = result.cfg_file

    access_interfaces = AccessInterfaceUtilization(result.ip_addr, cfg_file)
    print(access_interfaces.up_access_interfaces)

if __name__ == "__main__":
    main()
