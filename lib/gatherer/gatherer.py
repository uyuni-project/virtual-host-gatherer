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

from __future__ import print_function, absolute_import
import distutils.sysconfig
import sys
import os
import glob
import argparse
import json
import logging
import uuid
import importlib
from logging.handlers import RotatingFileHandler
from os.path import expanduser


def parse_options():
    """
    Supports the command-line arguments listed below.
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
    def __init__(self, opts):
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
        params = dict()
        if not self.modules:
            self._load_modules()
        for modname, mod in self.modules.items():
            params[modname] = mod.parameter()
            params[modname]['module'] = modname
        return params

    def run(self):
        if not self.modules:
            self._load_modules()

        with open(self.options.infile, 'r') as f:
            mgm_nodes = json.load(input_file)

        output = dict()
        for node in mgm_nodes:
            if 'module' not in node:
                self.log.error("Missing module definition in infile. Skipping")
                continue
            modname = node['module']
            if modname not in self.modules:
                self.log.error("Unsupported module '%s'. Skipping", modname)
                continue
            if not node['host']:
                self.log.error("Invalid 'host' entry. Skipping '%s'", node['name'])
                continue
            if not node['user'] or not node['pass']:
                self.log.error("Invalid 'user' or 'pass' entry. Skipping '%s'", node['name'])
                continue
            if 'id' not in node:
                ident = str(uuid.uuid4())
            else:
                ident = node['id']
            worker = self.modules[modname].worker(node)
            output[ident] = worker.run()
        if self.options.outfile:
            with open(self.options.outfile, 'w') as f:
                json.dump(output, f, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            print(json.dumps(output, sort_keys=True, indent=4, separators=(',', ': ')))

    def main(self):
        if self.options.verbose == 1:
            self.log.setLevel(logging.INFO)
        if self.options.verbose >= 2:
            self.log.setLevel(logging.DEBUG)

        if self.options.list_modules:
            installed_modules = self.list_modules()
            if self.options.outfile:
                with open(self.options.outfile, 'w') as f:
                    json.dump(installed_modules, f, sort_keys=True, indent=4, separators=(',', ': '))
            else:
                print(json.dumps(installed_modules, sort_keys=True, indent=4, separators=(',', ': ')))
            return

        if not self.options.infile:
            self.log.error("infile parameter required")
            return

        self.log.warning("Start scanning ...")
        self.run()
        self.log.warning("Scanning finished ...")

    def _load_modules(self):
        plib = distutils.sysconfig.get_python_lib()
        if os.path.exists('./lib/gatherer/modules/__init__.py'):
            plib = './lib'
        mod_path = "%s/gatherer/modules" % plib
        self.log.info("module path: %s", mod_path)
        filenames = glob.glob("%s/*.py" % mod_path)
        filenames = filenames + glob.glob("%s/*.pyc" % mod_path)
        filenames = filenames + glob.glob("%s/*.pyo" % mod_path)
        for fn in filenames:
            basename = os.path.basename(fn)
            if basename.startswith("__init__.py"):
                continue
            if basename[-3:] == ".py":
                modname = basename[:-3]
            elif basename[-4:] in [".pyc", ".pyo"]:
                modname = basename[:-4]

            try:
                self.log.debug("load %s", modname)
                mod = importlib.import_module('gatherer.modules.%s' % (modname))
                self.log.debug("DIR: %s", dir(mod))
                if not hasattr(mod, "parameter"):
                    self.log.error("Module %s has not a paramater function", modname)
                    continue
                if not hasattr(mod, "worker"):
                    self.log.error("Module %s has not a worker function", modname)
                    continue
                self.modules[modname] = mod
            except ImportError:
                raise
