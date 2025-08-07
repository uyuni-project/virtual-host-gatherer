# pylint: disable=invalid-name
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
import re
from gatherer.modules import WorkerInterface
from collections import OrderedDict

try:
    import kubernetes  # pylint: disable=import-self
    import kubernetes.client
    from kubernetes.client.rest import ApiException
    from urllib3.exceptions import HTTPError

    HAS_REQUIRED_MODULES = True
except ImportError as ex:
    HAS_REQUIRED_MODULES = False


class Kubernetes(WorkerInterface):
    """
    Worker class for the Kubernetes.
    """

    DEFAULT_PARAMETERS = OrderedDict([("kubeconfig", ""), ("context", "")])

    # pylint: disable-next=super-init-not-called
    def __init__(self):
        """
        Constructor.

        :return:
        """

        self.log = logging.getLogger(__name__)
        self.kubeconfig = self.context = None

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

        self.kubeconfig = node.get("kubeconfig")
        self.context = node.get("context")

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
                cpu = node.status.capacity.get("cpu")
                memory = 0
                reg = re.compile(r"^(\d+)(\w+)$")
                if reg.match(node.status.capacity.get("memory")):
                    memory, unit = reg.match(
                        node.status.capacity.get("memory")
                    ).groups()
                    if unit == "Ki":
                        memory = int(memory) / 1024
                    if unit == "Gi":
                        memory = int(memory) * 1024
                arch = node.status.node_info.architecture
                if arch.lower() == "amd64":
                    arch = "x86_64"

                output[node.metadata.name] = {
                    "type": "kubernetes",
                    "cpuArch": arch,
                    "cpuDescription": "(unknown)",
                    "cpuMhz": cpu,
                    "cpuVendor": "(unknown)",
                    "hostIdentifier": node.status.node_info.machine_id,
                    "name": node.metadata.name,
                    "os": node.status.node_info.os_image,
                    "osVersion": 1,
                    "ramMb": int(memory),
                    "totalCpuCores": cpu,
                    "totalCpuSockets": cpu,
                    "totalCpuThreads": 1,
                    "vms": {},
                }

        except (ApiException, HTTPError) as exc:
            if isinstance(exc, ApiException) and exc.status == 404:
                self.log.error("API Endpoint not found (404)")
                output = None
            else:
                self.log.exception(
                    "Exception when calling CoreV1Api->list_node: %s", exc
                )
                output = None

        return output

    def valid(self):
        """
        Check plugin class validity.

        :return: True if kubernetes module is installed.
        """

        return HAS_REQUIRED_MODULES

    def _setup_connection(self):
        """
        Setup and configure connection to Kubernetes
        """
        kubernetes.config.load_kube_config(
            config_file=self.kubeconfig, context=self.context
        )

    def _validate_parameters(self, node):
        """
        Validate parameters.

        :param node: Dictionary with the node description.
        :return:
        """

        if not (node.get("kubeconfig") and node.get("context")):
            raise AttributeError(
                "Missing parameter 'kubeconfig' and 'context' in infile"
            )
