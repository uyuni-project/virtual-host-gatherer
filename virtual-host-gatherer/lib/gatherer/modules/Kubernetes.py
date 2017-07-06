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
import tempfile
import os
import base64
import re
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
        self.user = node.get('username')
        self.password = node.get('password')
        self.client_cert = node.get('client-cert')
        self.client_key = node.get('client-key')
        self.ca_cert = node.get('ca-cert')

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
        self._setup_connection()
        try:
            api_instance = kubernetes.client.CoreV1Api()
            api_response = api_instance.list_node()

            for node in api_response.items:
                cpu = node.status.capacity.get('cpu')
                memory = 0
                reg = re.compile('^(\d+)(\w+)$')
                if reg.match(node.status.capacity.get('memory')):
                    memory, unit = reg.match(node.status.capacity.get('memory')).groups()
                    if unit == "Ki":
                        memory = int(memory) / 1024
                    if unit == "Gi":
                        memory = int(memory) * 1024
                arch = node.status.node_info.architecture
                if arch.lower() == "amd64":
                    arch = "x86_64"

                output[node.metadata.name] = {
                        'type': 'kubernetes',
                        'cpuArch': arch,
                        'cpuDescription': "(unknown)",
                        'cpuMhz': cpu,
                        'cpuVendor': "(unknown)",
                        'hostIdentifier': node.status.node_info.machine_id,
                        'name': node.metadata.name,
                        'os': node.status.node_info.os_image,
                        'osVersion': 1,
                        'ramMb': int(memory),
                        'totalCpuCores': cpu,
                        'totalCpuSockets': cpu,
                        'totalCpuThreads': 1,
                        'vms': {}
                        }

        except (ApiException, HTTPError) as exc:
            if isinstance(exc, ApiException) and exc.status == 404:
                self.log.error("API Endpoint not found (404)")
                return None
            else:
                self.log.exception(
                    'Exception when calling CoreV1Api->list_node: {0}'.format(exc)
                )
                return None

        finally:
            self._cleanup()
        return output

    def valid(self):
        """
        Check plugin class validity.

        :return: True if kubernetes module is installed.
        """

        return IS_VALID

    def _setup_connection(self):
        kubernetes.client.configuration.__init__()
        kubernetes.client.configuration.host = self.url
        kubernetes.client.configuration.user = self.user
        kubernetes.client.configuration.passwd = self.password
        if self.ca_cert:
            with tempfile.NamedTemporaryFile(prefix='kube-', delete=False) as ca:
                ca.write(base64.b64decode(self.ca_cert))
                kubernetes.client.configuration.ssl_ca_cert = ca.name
        if self.client_cert:
            with tempfile.NamedTemporaryFile(prefix='kube-', delete=False) as c:
                c.write(base64.b64decode(self.client_cert))
                kubernetes.client.configuration.cert_file = c.name
        if self.client_key:
            with tempfile.NamedTemporaryFile(prefix='kube-', delete=False) as k:
                k.write(base64.b64decode(self.client_key))
                kubernetes.client.configuration.key_file = k.name

    def _cleanup(self):
        ca = kubernetes.client.configuration.ssl_ca_cert
        cert = kubernetes.client.configuration.cert_file
        key = kubernetes.client.configuration.key_file
        if cert and os.path.exists(cert):
            Kubernetes._safe_rm(cert)
        if key and os.path.exists(key):
            Kubernetes._safe_rm(key)
        if ca and os.path.exists(ca):
            Kubernetes._safe_rm(ca)

    def _validate_parameters(self, node):
        """
        Validate parameters.

        :param node: Dictionary with the node description.
        :return:
        """

        if not node.get('url'):
            raise AttributeError("Missing parameter or value '{0}' in infile".format(url))

    @staticmethod
    def _safe_rm(tgt):
        '''
        Safely remove a file
        '''
        try:
            os.remove(tgt)
        except (IOError, OSError):
            pass

