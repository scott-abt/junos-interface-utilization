#!/usr/bin/env python

"""
Specifically written for Python 2.6 because that's what I have.

Get the % of utilized interfaces on the stack. Do not include feeds or other
non-access ports.
"""

# RPC calls can be returned in XML format in Junos by passing "| display xml"
# to the command. Can I use the json module to parse the XML to a dict?

import ConfigParser
class AccessInterfaceUtilization:
    """
    Object containing utilization stats of a switch
    """
    def __init__(self, device):
        self.creds = self.__createDefaults()
        if self.creds:
            self.u = self.creds[0]
            self.p = self.creds[1]

    def __createDefaults(self):
        try:
            self.config = ConfigParser.ConfigParser()
            self.config.readfp(open('default.ini'))
            return [self.config.get('DEFAULT', 'username'),
                self.config.get('DEFAULT', 'password')]
        except IOError as ioe:
            print("Could not open default.ini: {0}".format(ioe))
        except ConfigParser.Error as e:
            print("ConfigParser died: {0}".format(e))

def main():
    util = AccessInterfaceUtilization("tacos")

if __name__ == "__main__":
    main()
