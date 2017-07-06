# Copyright (c) 2017 SUSE LLC, Inc. All Rights Reserved.
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
Kubernetes Worker module implementation.
"""

from __future__ import print_function, absolute_import, division
import logging
from gatherer.modules import WorkerInterface
from collections import OrderedDict

try:
    import kubernetes  # pylint: disable=import-self
    import kubernetes.client
    from kubernetes.client.rest import ApiException
    from urllib3.exceptions import HTTPError
    IS_VALID = True
except ImportError as ex:
    IS_VALID = False


class Kubernetes(WorkerInterface):
    """
    Worker class for the Kubernetes.
    """

    DEFAULT_PARAMETERS = OrderedDict([
        ('url', ''),
        ('username', ''),
        ('password', ''),
        ('client-cert', ''),
        ('client-key', ''),
        ('ca-cert', '')])

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

        self.url = node['url']
        self.user = node['username']
        self.password = node['password']
        self.client_cert = node['client-cert']
        self.client_key = node['client-key']
        self.ca_cert = node['ca-cert']

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
        return output

    def valid(self):
        """
        Check plugin class validity.

        :return: True if pyVim module is installed.
        """

        return IS_VALID

    def _validate_parameters(self, node):
        """
        Validate parameters.

        :param node: Dictionary with the node description.
        :return:
        """

        if not node.get('url')
            raise AttributeError("Missing parameter or value '{0}' in infile".format(url))

