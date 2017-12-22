# Copyright (c) 2015 SUSE LLC, Inc. All Rights Reserved.
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
#
# http://pubs.vmware.com/vsphere-55/topic/com.vmware.wssdk.apiref.doc/right-pane.html

"""
VMWare Worker module implementation.
"""

from __future__ import print_function, absolute_import, division
import logging
import atexit
from gatherer.modules import WorkerInterface
from collections import OrderedDict

try:
    from pyVim.connect import SmartConnect, Disconnect
    IS_VALID = True
except ImportError as ex:
    IS_VALID = False


class VMware(WorkerInterface):
    """
    Worker class for the VMWare.
    """

    DEFAULT_PARAMETERS = OrderedDict([
        ('hostname', ''),
        ('port', 443),
        ('username', ''),
        ('password', '')])

    VMSTATE = {
        'poweredOff': 'stopped',
        'poweredOn': 'running',
        'suspended': 'paused'
    }

    def __init__(self):
        """
        Constructor.

        :return:
        """

        self.log = logging.getLogger(__name__)
        self.host = self.port = self.user = self.password = None

    # pylint: disable=R0801
    def set_node(self, node):
        """
        Set node information

        :param node: Dictionary of the node description.
        :return: void
        """

        try:
            self._validate_parameters(node)
        except AttributeError as error:
            self.log.error(error)
            raise error

        self.host = node['hostname']
        self.port = node.get('port', 443)
        self.user = node['username']
        self.password = node['password']

    def parameters(self):
        """
        Return default parameters

        :return: default parameter dictionary
        """

        return self.DEFAULT_PARAMETERS

    def __explore_nodes(self, node, output):
        """
        Explore tree nodes in depth and process hosts
        """
        try:
            if hasattr(node, 'hostFolder'):
                # child is now a "datacenter" and it can contain
                # clusters or folders.
                for child in node.hostFolder.childEntity:
                    self.__explore_nodes(child, output)
            elif hasattr(node, 'childEntity'):
                # vim.Folder
                for child in node.childEntity:
                    self.__explore_nodes(child, output)
            elif hasattr(node, "host"):
                # vim.Host
                self.__process_node(node, output)
        except Exception as exc:
            self.log.error("Unexpected error exploring nodes: {0}".format(exc))

    def __process_node(self, node, output):
        """
        Process parameters of a node and fill the output structure
        """
        try:
            # vim.ClusterComputeResource
            for host in node.host:
                host_name = host.summary.config.name.split()[0]
                mhz = (float(host.hardware.cpuInfo.hz) / float(1000 * 1000))
                ram = (int(host.hardware.memorySize / (1024 * 1024)))
                output[host_name] = {
                    'type': 'vmware',
                    'name': host_name,
                    'hostIdentifier': str(host),
                    'os': host.summary.config.product.name,
                    'osVersion': host.summary.config.product.version,
                    'totalCpuSockets': host.hardware.cpuInfo.numCpuPackages,
                    'totalCpuCores': host.hardware.cpuInfo.numCpuCores,
                    'totalCpuThreads': host.hardware.cpuInfo.numCpuThreads,
                    'cpuMhz': mhz,
                    'cpuVendor': host.hardware.cpuPkg[0].vendor,
                    'cpuDescription': host.hardware.cpuPkg[0].description.strip(),
                    'cpuArch': 'x86_64',
                    'ramMb': ram,
                    'vms': {},
                    'optionalVmData': {}
                }
                # If an additional hardware info is wanted:
                # print "pciDevice: %s" % host.hardware.pciDevice
                for virtual_machine in host.vm:
                    # print "Guest: %s" % vm.config.name
                    # print "Guest State: %s" % vm.runtime.powerState
                    # print "Guest CPUs: %s" % vm.summary.config.numCpu
                    # print "Guest RAM: %s" % vm.summary.config.memorySizeMB
                    # NOTE: 'vm.config is not always available. Skipping vm if an exception is raised.
                    # Ref: https://pubs.vmware.com/vi3/sdk/ReferenceGuide/vim.VirtualMachine.html
                    try:
                        vmname = virtual_machine.config.name
                        output[host_name]['vms'][vmname] = virtual_machine.config.uuid
                        output[host_name]['optionalVmData'][vmname] = {}
                        output[host_name]['optionalVmData'][vmname]['vmState'] = self.VMSTATE.get(
                            virtual_machine.runtime.powerState, 'unknown'
                        )
                    except AttributeError:
                        self.log.warning(
                            "Missing config for vm {0}. Skipping it.".format(virtual_machine.summary.vm)
                        )

        except (AttributeError, KeyError, IndexError) as exc:
            self.log.error("Unexpected error processing node: {0}".format(exc))

    def run(self):
        """
        Start worker.

        :return: Dictionary of the hosts in the worker scope.
        """

        self.log.info("Connect to %s:%s as user %s", self.host, self.port, self.user)
        try:
            connection = SmartConnect(host=self.host, user=self.user, pwd=self.password, port=int(self.port))
            atexit.register(Disconnect, connection)
        except IOError as ex:
            self.log.error(ex)
            connection = None
        if connection is None:
            self.log.error(
                "Could not connect to the specified host using specified "
                "username and password."
            )
            return

        content = connection.RetrieveContent()
        output = dict()
        for child in content.rootFolder.childEntity:
            self.__explore_nodes(child, output)
        Disconnect(connection)
        return output

    def valid(self):
        """
        Check plugin class validity.

        :return: True if pyVim module is installed.
        """

        return IS_VALID
