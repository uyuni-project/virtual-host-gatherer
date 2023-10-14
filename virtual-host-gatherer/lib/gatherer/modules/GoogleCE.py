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
Google Compute Engine Worker module implementation.
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


class GoogleCE(WorkerInterface):
    '''
    Worker class for the Google Compute Engine Public Cloud.
    '''

    DEFAULT_PARAMETERS = OrderedDict([
        ('service_account_email', ''),
        ('cert_path', ''),
        ('project_id', ''),
        ('zone', '')])

    def __init__(self):
        '''
        Constructor.

        :return:
        '''

        self.log = logging.getLogger(__name__)
        self.service_account_email = self.cert_path = self.project_id = self.zone = None

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

        self.service_account_email = node['service_account_email']
        self.cert_path = node['cert_path']
        self.project_id = node['project_id']
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
        self.log.info('Connect Google Compute Engine Public Cloud')
        try:
            cls = get_driver(Provider.GCE)
            driver = cls(self.service_account_email, self.cert_path, datacenter=self.zone,
                         project = self.project_id)
        except Exception as ex:
            self.log.error(ex)
            driver = None
        if driver is None:
            self.log.error(
                'Could not connect to the Google Compute Engine Public Cloud using specified '
                'credentials.'
            )
            return

        output = dict()
        output[self.node_id] = {
            'type': 'gce',
            'name': self.node_id,
            'hostIdentifier': self.node_id,
            'os': 'Google',
            'osVersion': 'GCE',
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
            if node.extra['zone'].name == self.zone:
                output[self.node_id]['vms'][node.name] = node.id
                output[self.node_id]['optionalVmData'][node.name] = {}
                output[self.node_id]['optionalVmData'][node.name]['vmState'] = str(node.state)
            else:
                skipped_regions.add(node.extra['zone'].name)

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
