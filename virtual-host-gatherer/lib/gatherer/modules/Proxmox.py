# Copyright (c) 2025 SUSE LLC, Inc. All Rights Reserved.
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

"""
Proxmox module implementation.
"""

from __future__ import print_function, absolute_import, division

import logging
from collections import OrderedDict
import importlib.util

from gatherer.modules import WorkerInterface

try:
    import proxmoxer

    # Check for HTTPS backend
    IS_VALID = importlib.util.find_spec("requests") is not None
except ImportError:
    IS_VALID = False


# pylint: disable=too-many-instance-attributes
class Proxmox(WorkerInterface):
    """
    Worker class for Libvirt.
    """

    DEFAULT_PARAMETERS = OrderedDict(
        [
            ("host", None),
            ("port", None),
            ("username", None),
            ("password", None),
            ("api_token_id", None),
            ("api_token_secret", None),
            ("verify_ssl", None),
        ]
    )

    def __init__(self):
        """
        Constructor.

        :return:
        """
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.uri = None
        self.host = None
        self.username = None
        self.password = None
        self.api_token_id = None
        self.api_token_secret = None
        self.verify_ssl = None
        self.token_auth = None

    # disable the duplicate code check
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

        self.uri = node.get("host") + ":" + str(node.get("port"))
        self.token_auth = bool(
            node.get("api_token_id") and node.get("api_token_secret")
        )
        if self.token_auth:
            self.api_token_id = node.get("api_token_id")
            self.api_token_secret = node.get("api_token_secret")
        else:
            self.username = node.get("username")
            self.password = node.get("password")
        if node.get("verify_ssl") is not None:
            self.verify_ssl = node.get("verify_ssl")
        else:
            self.verify_ssl = True

    def parameters(self):
        """
        Return default parameters

        :return: default parameter dictionary
        """

        return self.DEFAULT_PARAMETERS

    def run(self):
        """
        Start worker.
        """

        self.log.info("Using Proxmox API uri %s", self.uri)
        try:
            conn = self.get_connection()
            if conn:
                output = {}
                node_list = conn.nodes.get()
                if not node_list:
                    self.log.error("No nodes found in Proxmox cluster.")
                    return {}
                for node in node_list:
                    if node.get("status", "") != "online":
                        self.log.warning(
                            "Node %s is not online, skipping.", node["node"]
                        )
                        continue
                    output = self.process_node(conn, output, node["node"])
                return output
            self.log.error("Failed to connect to Proxmox API at %s", self.uri)
            return {}

        except (
            proxmoxer.ResourceException,
            proxmoxer.AuthenticationError,
            KeyError,
        ) as err:
            self.log.error(err)
            return {}

    def valid(self):
        """
        Check plugin class validity.

        :return: True if all components are installed
        """

        return IS_VALID

    def _validate_parameters(self, node):
        """
        Validate parameters.

        :param node: Dictionary with the node description.
        :return:
        """

        if not node.get("host"):
            raise AttributeError("Missing host parameter in infile")

        if not node.get("port"):
            raise AttributeError("Missing port parameter in infile")

        if not bool(node.get("username") and node.get("password")) ^ bool(
            node.get("api_token_id") and node.get("api_token_secret")
        ):
            raise AttributeError(
                "Either both username/password or api_token_id/api_token_secret must be set"
            )

        if node.get("verify_ssl") is not None and not isinstance(
            node.get("verify_ssl"), bool
        ):
            raise AttributeError(
                "Invalid value for verify_ssl parameter. Expected boolean."
            )

    def get_connection(self):
        """
        get connection object from libvirt module.

        :return: a :py:class:`ProxmoxAPI` instance on success.
        """

        # When using ssh transport, it is expected that the
        # ssh public key is copied onto the remote machine.
        conn = None
        try:
            if self.token_auth:
                # Use API token authentication
                self.log.info("Using API token authentication")
                conn = proxmoxer.ProxmoxAPI(
                    self.uri,
                    user=self.api_token_id,
                    token=self.api_token_secret,
                    verify_ssl=self.verify_ssl,
                )
            else:
                # Use username/password authentication
                self.log.info("Using username/password authentication")
                conn = proxmoxer.ProxmoxAPI(
                    self.uri,
                    user=self.username,
                    password=self.password,
                    verify_ssl=self.verify_ssl,
                )
        except proxmoxer.AuthenticationError as err:
            self.log.error(err)
        return conn

    def process_node(self, conn, output, node_name):
        """
        Process host/guest mapping info and fill the output structure

        :param conn: a :py:class:`ProxmoxAPI` instance
        :return: Dictionary with host/guest info
        """
        total_cpu_sockets = (
            conn.nodes(node_name).status.get().get("cpuinfo", {}).get("sockets", 0)
        )
        total_cpu_cores = (
            conn.nodes(node_name).status.get().get("cpuinfo", {}).get("cores", 0)
        )
        total_cpu_threads = (
            conn.nodes(node_name).status.get().get("cpuinfo", {}).get("cpus", 0)
        )
        cpu_mhz = conn.nodes(node_name).status.get().get("cpuinfo", {}).get("mhz", 0)

        output[node_name] = {
            "name": node_name,
            # Proxmox has no unique host identifier for nodes, using node name as identifier
            # could also used MAC address of the first network interface
            "hostIdentifier": node_name,
            "fallbackHostIdentifier": node_name,
            "totalCpuSockets": total_cpu_sockets,
            "totalCpuCores": total_cpu_cores,
            "totalCpuThreads": total_cpu_threads,
            "cpuMhz": cpu_mhz,
            # 'cpuVendor': Proxmox does not provide CPU vendor information as a easily accessible field
            "cpuDescription": conn.nodes(node_name)
            .status.get()
            .get("cpuinfo", {})
            .get("model", "unknown"),
            "cpuArch": "x86_64",  # Proxmox is only officially supported on x86_64 architecture
            "ramMb": conn.nodes(node_name)
            .status.get()
            .get("memory", {})
            .get("total", 0)
            // (1024**2),
            "vms": {},
            "optionalVmData": {},
            "os": "ProxmoxVE",
            "os_version": conn.nodes(node_name).version.get().get("release", "unknown"),
        }

        vm_list = conn.nodes(node_name).qemu.get()
        if not vm_list:
            self.log.warning("No VMs found on node %s", node_name)
        for vm_entry in vm_list:
            vm_name = vm_entry.get("name", "unknown")
            vm_id = vm_entry.get("vmid", "unknown")
            # WARNING: Multiple VMs can have the same name
            output[node_name]["vms"][vm_name] = vm_id
            output[node_name]["optionalVmData"][vm_name] = {
                "vmState": vm_entry.get("status", "unknown"),
                "proxmoxVmid": vm_id,
                "uptime": vm_entry.get("uptime", 0),
                "totalCpuThreads": vm_entry.get("cpus", 0),
                "memory": vm_entry.get("maxmem", 0) // (1024**2),
                "disk": vm_entry.get("maxdisk", 0) // (1024**2),
            }

        lxc_list = conn.nodes(node_name).lxc.get()
        if not lxc_list:
            self.log.warning("No LXC containers found on node %s", node_name)
            return output
        for lxc_entry in lxc_list:
            lxc_name = lxc_entry.get("name", "unknown")
            vm_id = lxc_entry.get("vmid", "unknown")
            # WARNING: Multiple LXC containers can have the same name
            output[node_name]["vms"][lxc_name] = vm_id
            output[node_name]["optionalVmData"][lxc_name] = {
                "vmState": lxc_entry.get("status", "unknown"),
                "proxmoxVmid": vm_id,
                "uptime": lxc_entry.get("uptime", 0),
                "totalCpuThreads": lxc_entry.get("cpus", 0),
                "memory": lxc_entry.get("maxmem", 0) // (1024**2),
                "disk": lxc_entry.get("maxdisk", 0) // (1024**2),
            }
        return output
