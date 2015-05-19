# Copyright (c) 2015 SUSE LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
TYPES = ['VMware', 'SUSECloud']

class Gatherer:
    def __init__(self):
        logfile = '/var/log/gatherer.log'
        self.log = logging.getLogger('')
        self.log.setLevel(logging.WARNING)
        formatFile = logging.Formatter("%(asctime)s %(name)s - %(levelname)s: %(message)s")
        formatStream = logging.Formatter("%(levelname)s: %(message)s")

        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatStream)
        self.log.addHandler(ch)

        if not os.access(logfile, os.W_OK):
            logfile = '/tmp/gatherer.log'

        fh = RotatingFileHandler(logfile,
                                 maxBytes=(1048576*5),
                                 backupCount=5)
        fh.setFormatter(formatFile)
        self.log.addHandler(fh)

    def _parseOptions(self):
        """
        Supports the command-line arguments listed below.
        """
        parser = argparse.ArgumentParser(
            description='Process args for retrieving all the Virtual Machines')
        parser.add_argument('-i', '--infile', required=True, action='store',
                            help='json input file')
        parser.add_argument('-o', '--outfile', required=True, action='store',
                            help='to write the output to (json)')
        parser.add_argument('-v', '--verbose', action='count',
                            help='increase log output verbosity')
        args = parser.parse_args()
        return args

    def loadPlugin(self, name):
        mod = __import__('modules', globals(), locals(), [str(name)])
        try:
            submod = getattr(mod, name)
        except AttributeError:
            self.log.error("Type %s is not supported. "
                           "Could not import gatherer.%s.", name, name)
            return
        self.log.debug("module %s loaded", name)
        return getattr(submod, "Worker")

    def main(self):
        output = list()
        options = self._parseOptions()
        if options.verbose == 1:
            self.log.setLevel(logging.INFO)
        if options.verbose >= 2:
            self.log.setLevel(logging.DEBUG)

        with open(options.infile, 'r') as f:
            mgmNodes = json.load(f)

        for node in mgmNodes:
            if node['type'] not in TYPES:
                self.log.error("Unsupported type '%s'. Skipping '%s'", node['type'], node['name'])
                continue
            if not node['host']:
                self.log.error("Invalid 'host' entry. Skipping '%s'", node['name'])
                continue
            if not node['user'] or not node['pass']:
                self.log.error("Invalid 'user' or 'pass' entry. Skipping '%s'", node['name'])
                continue
            plugin = self.loadPlugin(node['type'])
            if not plugin:
                continue
            worker = plugin(node)
            output.append(worker.run())
        with open(options.outfile, 'w') as f:
            json.dump(output, f, sort_keys=True, indent=4, separators=(',', ': '))
