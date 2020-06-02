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
from gatherer.modules import WorkerInterface
from collections import OrderedDict


IS_VALID = True


class NutanixAHV(WorkerInterface):
    """
    Worker class for NutanixAHV.
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
        output = dict()
        return output

    def valid(self):
        """
        Check plugin class validity.

        :return: True if pyVim module is installed.
        """
        return IS_VALID
