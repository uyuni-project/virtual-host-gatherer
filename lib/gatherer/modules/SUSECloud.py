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

from __future__ import print_function, absolute_import
import json
import logging
from novaclient.v1_1 import client


class SUSECloudWorker(object):
    """
    Worker class for the SUSE Cloud.
    """

    def __init__(self, node):
        """
        Constructor.

        :param node: Dictionary of the node description.
        :return:
        """

        self.log = logging.getLogger(__name__)
        for k in parameter():
            if k not in node:
                self.log.error("Missing parameter '%s' in infile", k)
                raise AttributeError("Missing parameter '%s' in infile" % k)

        self.host = node['host']
        self.port = node.get('port', 5000)
        self.user = node['user']
        self.password = node['pass']
        self.tenant = node['tenant']

    def run(self):
        """
        Start worker.
        :return: Dictionary of the hosts in the worker scope.
        """

        output = dict()
        url = "http://%s:%s/v2.0/" % (self.host, self.port)
        self.log.info("Connect to %s for tenant %s as user %s", url, self.tenant, self.user)
        cloud_client = client.Client(self.user, self.password, self.tenant, url, service_type="compute")
        for hyp in cloud_client.hypervisors.list():
            cpu_info = json.loads(hyp.cpu_info)
            output[hyp.hypervisor_hostname] = {
                'name': hyp.hypervisor_hostname,
                'os': hyp.hypervisor_type,
                'osVersion': hyp.hypervisor_version,
                'sockets': cpu_info.get('topology', {}).get('sockets'),
                'cores': cpu_info.get('topology', {}).get('cores'),
                'threads': cpu_info.get('topology', {}).get('threads'),
                'ghz': 0,
                'cpuVendor': cpu_info.get('vendor'),
                'cpuDescription': cpu_info.get('model'),
                'cpuArch': cpu_info.get('arch'),
                'ram': hyp.memory_mb,
                'vms': {}
            }
            for result in cloud_client.hypervisors.search(hyp.hypervisor_hostname, True):
                if hasattr(result, 'servers'):
                    for vm in result.servers:
                        output[hyp.hypervisor_hostname]['vms'][vm['name']] = vm['uuid']

        return output


def parameter():
    return {
        'host': '',
        'port': 5000,
        'user': '',
        'pass': '',
        'proto': 'https',
        'tenant': 'openstack'
    }


def worker(node):
    """
    Create new worker.

    :param node: Node description
    :return: SUSECloudWorker object
    """

    return SUSECloudWorker(node)
