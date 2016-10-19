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
            if hasattr(child, 'hostFolder'):
                # child is now a "datacenter"
                cluster_list = child.hostFolder.childEntity
                for cluster in cluster_list:
                    for host in cluster.host:
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
                            'vms': {}
                        }
                        # If an additional hardware info is wanted:
                        # print "pciDevice: %s" % host.hardware.pciDevice
                        for virtual_machine in host.vm:
                            # print "Guest: %s" % vm.config.name
                            # print "Guest State: %s" % vm.runtime.powerState
                            # print "Guest CPUs: %s" % vm.summary.config.numCpu
                            # print "Guest RAM: %s" % vm.summary.config.memorySizeMB
                            output[host_name]['vms'][virtual_machine.config.name] = virtual_machine.config.uuid
        Disconnect(connection)
        return output

    def valid(self):
        """
        Check plugin class validity.

        :return: True if pyVim module is installed.
        """

        return IS_VALID
