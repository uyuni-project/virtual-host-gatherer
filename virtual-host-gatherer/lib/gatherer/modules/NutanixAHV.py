# Copyright (c) 2020 SUSE LLC, Inc. All Rights Reserved.                                                                                                                 
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
NutanixAHV Worker module implementation.
"""

from __future__ import print_function, absolute_import
import logging
import base64
import json
from gatherer.modules import WorkerInterface
from collections import OrderedDict
import ssl

try:
    try:
        from urllib.request import urlopen, Request
    except ImportError:
        from urllib2 import urlopen, Request
    IS_VALID = True
except ImportError:
    IS_VALID = False


_PRISM_V2_API_PREFIX = 'PrismGateway/services/rest/v2.0/'
_PRISM_V2_API_HOSTS_ENDPOINT = _PRISM_V2_API_PREFIX + 'hosts'
_PRISM_V2_API_VMS_ENDPOINT = _PRISM_V2_API_PREFIX + 'vms'


class NutanixAHV(WorkerInterface):
    """
    Worker class for NutanixAHV.
    """

    DEFAULT_PARAMETERS = OrderedDict([
        ('hostname', ''),
        ('port', 9440),
        ('username', ''),
        ('password', '')])

    VMSTATE = {
        'off': 'stopped',
        'on': 'running',
        'powering_on': 'powering_on',
        'shutting_down': 'shutting_down' ,
        'powering_off': 'powering_off',
        'pausing': 'pausing',
        'suspending': 'suspending' ,
        'suspended': 'suspended',
        'resuming': 'resuming',
        'resetting': 'resetting',
        'migrating': 'migrating',
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
        self.port = node.get('port', 9440)
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
        self.log.info("Connect to %s:%s as user %s", self.host, self.port, self.user)

        base_url = "https://%s:%s/" % (self.host, self.port)
        auth_b64 = base64.b64encode('{}:{}'.format(self.user, self.password).encode()).decode()

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            req = Request(base_url + _PRISM_V2_API_HOSTS_ENDPOINT)
            req.add_header("Authorization", "Basic %s" % auth_b64)
            hosts_list = json.load(urlopen(req, context=ctx))

            req = Request(base_url + _PRISM_V2_API_VMS_ENDPOINT)
            req.add_header("Authorization", "Basic %s" % auth_b64)
            vms_list = json.load(urlopen(req, context=ctx))

            for host in hosts_list['entities']:
                output[host['name']] = {
                    'name': host['name'],
                    'hostIdentifier': host['name'],
                    'type': 'nutanix',
                    'os': 'Nutanix AHV',
                    'osVersion': host['hypervisor_full_name'],
                    'totalCpuSockets': host['num_cpu_sockets'],
                    'totalCpuCores': host['num_cpu_cores'],
                    'totalCpuThreads': host['num_cpu_threads'],
                    'cpuMhz': int(host['cpu_capacity_in_hz'] / 1000 / 1000),
                    'cpuVendor': host['cpu_model'],
                    'cpuDescription': host['cpu_model'],
                    'cpuArch': "x86_64",
                    'ramMb': int(host['memory_capacity_in_bytes'] / 1000 / 1000),
                    'vms': {},
                    'optionalVmData': {}
                }

                for vm in filter(lambda x: x['host_uuid'] == host['uuid'], vms_list['entities']):
                    output[host['name']]['vms'][vm['name']] = vm['uuid']
                    output[host['name']]['optionalVmData'][vm['name']] = {}
                    output[host['name']]['optionalVmData'][vm['name']]['vmState'] = self.VMSTATE.get(vm['power_state'], 'unknown')

        except Exception as exc:
            self.log.error(exc)

        return output

    def valid(self):
        """
        Check plugin class validity.

        :return: True if pyVim module is installed.
        """
        return IS_VALID
