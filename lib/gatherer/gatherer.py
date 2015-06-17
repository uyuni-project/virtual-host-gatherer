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

"""
Main Gatherer application implementation.
"""

from __future__ import print_function, absolute_import
import sys
import os
import argparse
import json
import logging
import uuid
from logging.handlers import RotatingFileHandler
from os.path import expanduser


def parse_options():
    """
    Parse command line options.
    """

    home = expanduser("~")
    if home == '/root':
        home = '/var/log'
    log_destination = "%s/gatherer.log" % home
    parser = argparse.ArgumentParser(
        description='Process args for retrieving all the Virtual Machines')
    parser.add_argument(
        '-i', '--infile', action='store',
        help='json input file'
    )
    parser.add_argument(
        '-o', '--outfile', action='store',
        help='to write the output (json) file instead of stdout'
    )
    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help='increase log output verbosity'
    )
    parser.add_argument(
        '-l', '--list-modules', action='store_true',
        help="list modules with options"
    )
    parser.add_argument(
        '-L', '--logfile', action='store',
        default=log_destination,
        help="path to logfile. Default: %s" % log_destination
    )

    return parser.parse_args()


class Gatherer(object):
    """
    Gatherer class.
    """

    def __init__(self, opts):
        """
        Constructor.
        :param opts: Command line options.
        :return:
        """

        self.options = opts
        self.log = logging.getLogger('')
        self.log.setLevel(logging.WARNING)

        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        self.log.addHandler(stream_handler)

        file_handler = RotatingFileHandler(self.options.logfile, maxBytes=(0x100000 * 5), backupCount=5)
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(name)s - %(levelname)s: %(message)s"))
        self.log.addHandler(file_handler)

        self.modules = dict()

    def list_modules(self):
        """
        List available modules.

        :return: Dictionary of available modules.
        """

        params = dict()
        if not self.modules:
            self._load_modules()
        for modname, mod in self.modules.items():
            params[modname] = mod.parameters
            params[modname]['module'] = modname
        return params

    def _run(self):
        """
        Run gatherer application.

        :return: void.
        """

        if not self.modules:
            self._load_modules()

        with open(self.options.infile) as input_file:
            mgm_nodes = json.load(input_file)

        output = dict()
        for node in mgm_nodes:
            if 'module' not in node:
                self.log.error("Skipping undefined module in the input file.")
                continue
            modname = node['module']
            if modname not in self.modules:
                self.log.error("Skipping unsupported module '%s'.", modname)
                continue
            if not node['host']:
                self.log.error("Invalid 'host' entry. Skipping '%s'", node['name'])
                continue
            if not node['user'] or not node['pass']:
                self.log.error("The 'user' or 'pass' entry is missing. Skipping '%s'", node['name'])
                continue

            worker = self.modules[modname].worker(node)
            output[node.get("id", str(uuid.uuid4()))] = worker.run()

        if self.options.outfile:
            with open(self.options.outfile, 'w') as input_file:
                json.dump(output, input_file, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            print(json.dumps(output, sort_keys=True, indent=4, separators=(',', ': ')))

    def main(self):
        """
        Application start.
        :return:
        """

        if self.options.verbose == 1:
            self.log.setLevel(logging.INFO)
        if self.options.verbose >= 2:
            self.log.setLevel(logging.DEBUG)

        if self.options.list_modules:
            installed_modules = self.list_modules()
            if self.options.outfile:
                with open(self.options.outfile, 'w') as output_file:
                    json.dump(installed_modules, output_file, sort_keys=True, indent=4, separators=(',', ': '))
            else:
                print(json.dumps(installed_modules, sort_keys=True, indent=4, separators=(',', ': ')))
            return

        if not self.options.infile:
            self.log.error("Input file was not specified")
            return

        self.log.warning("Scanning began")
        self._run()
        self.log.warning("Scanning finished")

    def _load_modules(self):
        """
        Load available modules for the gatherer.
        If module meets the description, but cannot be imported, the ImportError exception is raised.

        :return: void
        """
        mod_path = os.path.dirname(__import__('gatherer.modules', globals(), locals(), ['gatherer'], 0).__file__)
        self.log.info("module path: %s", mod_path)
        for module_name in [item for item in os.listdir(mod_path)
                            if item.endswith(".py") and not item.startswith("__init__")]:
            try:
                self.log.debug('Loading module "%s"', module_name)
                mod = __import__('gatherer.modules.{0}'.format(module_name), globals(), locals(), ['gatherer', 'modules'], 0)
                self.log.debug("Introspection: %s", dir(mod))
                if not hasattr(mod, "worker"):
                    self.log.error('Missing function "worker" in the module "%s"!', module_name)
                    continue
                self.modules[module_name] = mod
            except ImportError:
                self.log.debug('Module "%s" was not loaded.', module_name)
                raise
