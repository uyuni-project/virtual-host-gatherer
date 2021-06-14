# Copyright (c) 2021 SUSE LLC, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Xen Worker module implementation.
"""

from __future__ import print_function, absolute_import
import logging
from collections import OrderedDict
from gatherer.modules import WorkerInterface

try:
    import XenAPI
    IS_VALID = True
except ImportError:
    IS_VALID = False



class Xen(WorkerInterface):
    """
    Worker class for Xen.
    """

    DEFAULT_PARAMETERS = OrderedDict([
        ('hostname', ''),
        ('port', '443'),
        ('username', ''),
        ('password', '')])

    VMSTATE = {
        'Halted': 'stopped',
        'Running': 'running',
        'Paused': 'paused',
        'Suspended': 'suspended',
    }

    def __init__(self):
        """
        Constructor.

        :return:
        """

        self.log = logging.getLogger(__name__)
        self.host = self.port = self.user = self.password = None

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
        self.port = node['port']
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
        output = dict()
        self.log.info('Connect Xen Server %s:%s as user %s', self.host, self.port, self.user)
        try:
            protocol = 'https' if self.port == 443 else 'http'
            session = XenAPI.Session("%s://%s:%s" % (protocol, self.host, self.port))
            session.xenapi.login_with_password(self.user, self.password, "2.3", "Xen Gatherer")

            # Dictionary {opaque_reference: host_data}
            hosts = {ref: session.xenapi.host.get_record(ref) for ref in session.xenapi.host.get_all()}
            for host in hosts.values():
                self.log.debug('Host=%s, uuid=%s', host["name_label"], host["uuid"])

            vms = []
            for vm_ref in session.xenapi.VM.get_all():
                vm = session.xenapi.VM.get_record(vm_ref)
                if not vm['is_a_template']:
                    vms.append(vm)

            for ref, host in hosts.items():
                output[host['name_label']] = {
                    'name': host['name_label'],
                    'hostIdentifier': host['name_label'],
                    'type': 'xen',
                    'os': 'citrixhypervisor',
                    'osVersion': host['software_version']['product_version'],
                    'totalCpuSockets': host['cpu_info']['socket_count'],
                    'totalCpuCores': host['cpu_info']['cpu_count'],
                    'totalCpuThreads': 1,
                    'cpuMhz': float(host['cpu_info']['speed']),
                    'cpuDescription': host['cpu_info']['modelname'],
                    'cpuArch': "x86_64",
                    'ramMb': int(session.xenapi.host_metrics.get_record(host['metrics'])['memory_total']) / (1024 * 1024),
                    'vms': {},
                    'optionalVmData': {}
                }

                for vm in filter(lambda x: x['resident_on'] == ref, vms):
                    output[host['name_label']]['vms'][vm['name_label']] = vm['uuid']
                    output[host['name_label']]['optionalVmData'][vm['name_label']] = {}
                    output[host['name_label']]['optionalVmData'][vm['name_label']]['vmState'] = self.VMSTATE.get(vm['power_state'], 'unknown')

            output['Xen-DetachedVMs'] = {
                'name': "Xen-DetachedVMs",
                'hostIdentifier': "Xen-DetachedVMs",
                'type': 'xen',
                'os': 'citrixhypervisor',
                'osVersion': "Fake Host",
                'totalCpuSockets': 0,
                'totalCpuCores': 0,
                'totalCpuThreads': 0,
                'cpuMhz': 0,
                'cpuDescription': "Fake Host",
                'cpuArch': "x86_64",
                'ramMb': 0,
                'vms': {},
                'optionalVmData': {}
            }
            for vm in filter(lambda x: x['resident_on'] == 'OpaqueRef:NULL', vms):
                output[host['name_label']]['vms'][vm['name_label']] = vm['uuid']
                output[host['name_label']]['optionalVmData'][vm['name_label']] = {}
                output[host['name_label']]['optionalVmData'][vm['name_label']]['vmState'] = self.VMSTATE.get(vm['power_state'], 'unknown')

        except Exception as ex:
            self.log.exception('Unable to fetch data from Xen Server: {0}'.format(ex))
            output = None


        return output

    def valid(self):
        """
        Check plugin class validity.

        :return: True if XenAPI module is installed.
        """
        return IS_VALID
