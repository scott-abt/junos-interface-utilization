#!/usr/bin/env python

"""
Retrieves the number of utilized access ports on a Juniper EX switch.

Specifically written for Python 2.6 because that's what I have. Get the number
of utilized interfaces on the stack. Do not include feeds or other non-access 
ports.
"""

import xmltodict, re
from netmiko import ConnectHandler
from argparse import ArgumentParser as AP
from xml.parsers.expat import ExpatError

try:
    from mycreds import the_creds
except ImportError as ie:
    print("\n\n***You must provide mycreds.py in this directory. See example_creds.py for format.***\n\n")
    raise


class AccessInterfaceUtilization:
    
    """
    Currently only counts ge-* interfaces in an 'up' state.
    Does not count 'tagged' interfaces.
    """

    def __init__(self, conn, switch_dict):
        self.conn = conn
        self.switch_dict = switch_dict
        self.op_rpc = (
                'show ethernet-switching interfaces detail | display xml')
        self.xml_output = self.conn.send_command(self.op_rpc)

        if self.switch_dict['username'] == "root":
            self.clean_xml = str(self.xml_output).partition("\n")[2]
        else:
            self.clean_xml = str(self.xml_output).strip().partition("\n")[2]\

        if self.clean_xml:
            try:
                self.dict_of_xml = xmltodict.parse(self.clean_xml)
            except ExpatError:
                try:
                    self.dict_of_xml = xmltodict.parse(self.xml_output)
                except:
                    raise

            self.up_access_interfaces = 0
            for interface in self.dict_of_xml['rpc-reply']['switching-interface-information']['interface']:
                self.gige_re = re.compile('ge-.*')
                if (self.gige_re.match(interface['interface-name']) and
                        interface['interface-port-mode'] == "Access" and
                        interface['interface-state'] == "up"):
                    self.up_access_interfaces += 1
        else:
            print("I connected, but no valid response was received from the "
                  "switch. Here's the raw output:<snip>\n{0}".format(self.xml_output))
            print("</snip>")
            raise ValueError


    def get_utilization(self):
        return self.up_access_interfaces


def main():

    arg_parser = AP()
    arg_parser.add_argument('-i', dest='ip_addr', help="IP address or FQDN "
                            "of the switch")
    
    args = arg_parser.parse_args()

    fails = 0
    success = 0
    for cred_set in the_creds:
        if (success > 0):
            continue
        for username, password in cred_set.items():
            switch_dict = {
                'device_type': 'juniper',
                'ip': args.ip_addr,
                'username': username,
                'password': password,
                'verbose': False,
            }
            
            try:
                conn = ConnectHandler(**switch_dict)
            except:
                fails += 1
                continue
                
            utilization = AccessInterfaceUtilization(conn, switch_dict)
            try:
                print(utilization.get_utilization())
                success =+ 1
            except:
                raise


if __name__ == "__main__":
    main()
