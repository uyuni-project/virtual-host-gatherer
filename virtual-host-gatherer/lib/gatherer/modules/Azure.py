# Copyright (c) 2019 SUSE LLC, Inc. All Rights Reserved.
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

'''
Azure Cloud Worker module implementation.
'''

from __future__ import print_function, absolute_import, division
import logging
from gatherer.modules import WorkerInterface
from collections import OrderedDict

try:
    from libcloud.compute.types import Provider
    from libcloud.compute.providers import get_driver
    IS_VALID = True
except ImportError as ex:
    IS_VALID = False


class Azure(WorkerInterface):
    '''
    Worker class for the Azure Public Cloud.
    '''

    DEFAULT_PARAMETERS = OrderedDict([
        ('subscription_id', ''),
        ('application_id', ''),
        ('tenant_id', ''),
        ('secret_key', ''),
        ('zone', '')])

    def __init__(self):
        '''
        Constructor.

        :return:
        '''

        self.log = logging.getLogger(__name__)
        self.subscription_id = self.application_id = self.tenant_id = self.secret_key = self.zone = None

    # pylint: disable=R0801
    def set_node(self, node):
        '''
        Set node information

        :param node: Dictionary of the node description.
        :return: void
        '''

        try:
            self._validate_parameters(node)
        except AttributeError as error:
            self.log.error(error)
            raise error

        self.subscription_id = node['subscription_id']
        self.application_id = node['application_id']
        self.tenant_id = node['tenant_id']
        self.secret_key = node['secret_key']
        self.zone = node['zone']
        self.node_id = node['id']

    def parameters(self):
        '''
        Return default parameters

        :return: default parameter dictionary
        '''

        return self.DEFAULT_PARAMETERS

    def run(self):
        '''
        Start worker.

        :return: Dictionary of the hosts in the worker scope.
        '''
        self.log.info('Connect Azure Public Cloud')
        try:
            cls = get_driver(Provider.AZURE_ARM)
            driver = cls(tenant_id=self.tenant_id, subscription_id=self.subscription_id,
                         key=self.application_id, secret=self.secret_key)
        except Exception as ex:
            self.log.error(ex)
            driver = None
        if driver is None:
            self.log.error(
                'Could not connect to the Azure Public Cloud using specified '
                'credentials.'
            )
            return

        output = dict()
        output[self.node_id] = {
            'type': 'azure',
            'name': self.node_id,
            'hostIdentifier': self.node_id,
            'os': 'Azure',
            'osVersion': 'Azure Cloud',
            'totalCpuCores': 0,
            'totalCpuSockets': 0,
            'ramMb': 0,
            'cpuArch': 'cloud',
            'cpuMhz': 0,
            'vms' : {},
            'optionalVmData': {}
        }

        for node in driver.list_nodes():
            if node.extra['location'] == self.zone:
                output[self.node_id]['vms'][node.name] = node.extra['properties']['vmId']
                output[self.node_id]['optionalVmData'][node.name] = {}
                output[self.node_id]['optionalVmData'][node.name]['vmState'] = node.state
        return output

    def valid(self):
        '''
        Check plugin class validity.

        :return: True if libcloud module is installed.
        '''

        return IS_VALID
