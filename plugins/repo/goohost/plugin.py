#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information
'''

from __future__ import with_statement
from plugins import core
import socket
import sys
import re
import os

current_path = os.path.abspath(os.getcwd())

__author__ = "Francisco Amato"
__copyright__ = "Copyright (c) 2013, Infobyte LLC"
__credits__ = ["Francisco Amato"]
__license__ = ""
__version__ = "1.0.0"
__maintainer__ = "Francisco Amato"
__email__ = "famato@infobytesec.com"
__status__ = "Development"

class GoohostParser(object):
    """
    The objective of this class is to parse an xml file generated by the goohost tool.

    TODO: Handle errors.
    TODO: Test goohost output version. Handle what happens if the parser doesn't support it.
    TODO: Test cases.

    @param goohost_filepath A proper simple report generated by goohost
    @param goohost_scantype You could select scan type ip, mail or host
    """
    def __init__(self, goohost_filepath, goohost_scantype):
        self.filepath = goohost_filepath
        self.scantype = goohost_scantype

        with open(self.filepath, "r") as f:

            line = f.readline()
            self.items = []
            while line:
                if self.scantype == 'ip':
                    minfo = line.split()
                    item = {'host': minfo[0], 'ip': minfo[1]}
                elif self.scantype == 'host':
                    line = line.strip()
                    item = {'host': line, 'ip': self.resolve(line)}
                else:
                    item = {'data': line}

                self.items.append(item)
                line = f.readline()

    def resolve(self, host):
        try:
            return socket.gethostbyname(host)
        except:
            pass
        return host


class GoohostPlugin(core.PluginBase):
    """
    Example plugin to parse goohost output.
    """
    def __init__(self):
        core.PluginBase.__init__(self)
        self.id = "Goohost"
        self.name = "Goohost XML Output Plugin"
        self.plugin_version = "0.0.1"
        self.version = "v.0.0.1"
        self.options = None
        self._current_output = None
        self._current_path = None
        self._command_regex = re.compile(
            r'^(sudo goohost\.sh|goohost\.sh|sh goohost\.sh|\.\/goohost\.sh).*?')
        self.scantype = "host"
        self.host = None

        global current_path
        self.output_path = None

    def parseOutputString(self, output, debug=False):
        """
        This method will discard the output the shell sends, it will read it from
        the xml where it expects it to be present.

        NOTE: if 'debug' is true then it is being run from a test case and the
        output being sent is valid.
        """

        if self.output_path is None:
            mypath = re.search("Results saved in file (\S+)", output)
            if mypath is not None:
                self.output_path = self._current_path + "/" + mypath.group(1)
            else:
                return False

        if debug:
            parser = GoohostParser(output, self.scantype)
        else:
            if not os.path.exists(self.output_path):
                return False

            parser = GoohostParser(self.output_path, self.scantype)

            if self.scantype == 'host' or self.scantype == 'ip':
                for item in parser.items:
                    h_id = self.createAndAddHost(item['ip'])
                    i_id = self.createAndAddInterface(
                        h_id,
                        item['ip'],
                        ipv4_address=item['ip'],
                        hostname_resolution=item['host'])

        del parser

    def processCommandString(self, username, current_path, command_string):
        """
        Set output path for parser...
        """
        self._current_path = current_path

    def setHost(self):
        pass


def createPlugin():
    return GoohostPlugin()

if __name__ == '__main__':
    parser = GoohostParser(sys.argv[1])
    for item in parser.items:
        if item.status == 'up':
            print item
