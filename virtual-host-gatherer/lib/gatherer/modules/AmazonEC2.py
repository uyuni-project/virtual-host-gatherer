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
Amazon EC2 Worker module implementation.
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


class AmazonEC2(WorkerInterface):
    '''
    Worker class for the Amazon EC2 Public Cloud.
    '''

    DEFAULT_PARAMETERS = OrderedDict([
        ('access_key_id', ''),
        ('secret_access_key', ''),
        ('region', ''),
        ('zone', '')])

    def __init__(self):
        '''
        Constructor.

        :return:
        '''

        self.log = logging.getLogger(__name__)
        self.access_key_id = self.secret_access_key = self.region = self.zone = None

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

        self.access_key_id = node['access_key_id']
        self.secret_access_key = node['secret_access_key']
        self.region = node['region']
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
        self.log.info('Connect Amazon EC2 Public Cloud')
        try:
            cls = get_driver(Provider.EC2)
            driver = cls(self.access_key_id, self.secret_access_key,
                         region=self.region)
        except Exception as ex:
            self.log.error(ex)
            driver = None
        if driver is None:
            self.log.error(
                'Could not connect to the Amazon EC2 Public Cloud using specified '
                'credentials.'
            )
            return

        output = dict()
        output[self.node_id] = {
            'type': 'aws',
            'name': self.node_id,
            'hostIdentifier': self.node_id,
            'os': 'Amazon AWS',
            'osVersion': 'EC2',
            'totalCpuCores': 0,
            'totalCpuSockets': 0,
            'ramMb': 0,
            'cpuArch': 'cloud',
            'cpuMhz': 0,
            'vms' : {},
            'optionalVmData': {}
        }

        skipped_regions = set()
        for node in driver.list_nodes():
            if node.extra['availability'] == self.zone:
                output[self.node_id]['vms'][node.name] = node.id
                output[self.node_id]['optionalVmData'][node.name] = {}
                output[self.node_id]['optionalVmData'][node.name]['vmState'] = str(node.state)
            else:
                skipped_regions.add(node.extra['availability'])

        if skipped_regions:
            self.log.info("Found nodes in other regions than {}".format(self.zone))
            self.log.info("Skipped regions: {}".format(skipped_regions))
        return output

    def valid(self):
        '''
        Check plugin class validity.

        :return: True if libcloud module is installed.
        '''

        return IS_VALID
