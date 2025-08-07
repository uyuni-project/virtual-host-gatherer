# pylint: disable=invalid-name
# Copyright (c) 2022 SUSE LLC, Inc. All Rights Reserved.
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
Libvirt Worker module implementation.
"""

from __future__ import print_function, absolute_import, division
import logging
from collections import OrderedDict
from xml.etree import ElementTree
from gatherer.modules import WorkerInterface
from six.moves import urllib


try:
    import libvirt

    IS_VALID = True
except ImportError as ex:
    IS_VALID = False


class Libvirt(WorkerInterface):
    """
    Worker class for Libvirt.
    """

    DEFAULT_PARAMETERS = OrderedDict(
        [("uri", ""), ("sasl_username", None), ("sasl_password", None)]
    )

    # pylint: disable-next=super-init-not-called
    def __init__(self):
        """
        Constructor.

        :return:
        """

        super().__init__()
        self.log = logging.getLogger(__name__)
        self.uri = None
        self.sasl_username = None
        self.sasl_password = None

        if self.valid():
            self.VMSTATE = {
                libvirt.VIR_DOMAIN_RUNNING: "running",
                libvirt.VIR_DOMAIN_BLOCKED: "idle",
                libvirt.VIR_DOMAIN_PAUSED: "paused",
                libvirt.VIR_DOMAIN_SHUTDOWN: "in shutdown",
                libvirt.VIR_DOMAIN_SHUTOFF: "shut off",
                libvirt.VIR_DOMAIN_CRASHED: "crashed",
                libvirt.VIR_DOMAIN_NOSTATE: "no state",
            }

    # pylint: disable=R0801
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

        splitted_url = urllib.parse.urlsplit(node.get("uri"))

        if splitted_url.query:
            self.uri = node.get("uri") + "&no_tty=1"
        else:
            self.uri = node.get("uri") + "?no_tty=1"

        self.sasl_username = node.get("sasl_username")
        self.sasl_password = node.get("sasl_password")

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

        self.log.info("Using libvirt uri %s", self.uri)
        try:
            conn = self.get_connection()
            if conn:
                output = self.get_host_guest_mapping(conn)
                return output
        except libvirt.libvirtError as err:
            self.log.error(err)
        finally:
            if conn:
                conn.close()

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

        if not node.get("uri"):
            raise AttributeError("Missing uri parameter in infile")

        splitted_url = urllib.parse.urlsplit(node.get("uri"))

        if not splitted_url.scheme:
            raise AttributeError(
                "Missing scheme in uri. Few examples of a valid scheme: qemu, qemu+ssh, qemu+tcp"
            )

        if len(splitted_url.path) < 1:
            raise AttributeError("path to libvirt not specified in the uri")

    def get_connection(self):
        """
        get connection object from libvirt module.

        :return: a :py:class:`virConnect` instance on success.
        """

        # When using ssh transport, it is expected that the
        # ssh public key is copied onto the remote machine.
        conn = None
        try:
            if self.sasl_username and self.sasl_password:
                # username/password authentication with SASL
                user_data = [self.sasl_username, self.sasl_password]
                auth = [
                    [libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE],
                    self.request_cred,
                    user_data,
                ]
                flags = libvirt.VIR_CONNECT_RO
                conn = libvirt.openAuth(self.uri, auth, flags)
            else:
                conn = libvirt.openReadOnly(self.uri)
        except libvirt.libvirtError as err:
            self.log.error(err)
        return conn

    @staticmethod
    def get_host_capabilities(conn):
        """
        Get information about the capabilities of the host

        :param conn: a :py:class:`virConnect` instance
        :return: xml representation of the virConnectGetCapabilities output
        """

        return ElementTree.fromstring(conn.getCapabilities())

    @staticmethod
    def get_host_cpu_topology(capabilities_xml):
        """
        Get information about the host cpu topology

        :param capabilities_xml: xml representation of the virConnectGetCapabilities
        :return: xml representation of the host topology
        """

        return capabilities_xml.find("host/cpu/topology")

    @staticmethod
    def get_host_memory(conn):
        """
        Get information about the memory of the host

        :param conn: a :py:class:`virConnect` instance
        :return: memory in Megabyte

        """
        buf = conn.getMemoryStats(
            cellNum=libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS, flags=0
        )
        return float(buf.get("total", 0)) / 1024

    def get_host_guest_mapping(self, conn):
        """
        Process host/guest mapping info and fill the output structure

        :param conn: a :py:class:`virConnect` instance
        :return: Dictionary with host/guest info
        """

        output = {}
        try:
            hypervisor_hostname = conn.getHostname()
            libversion = conn.getLibVersion()
            maj = int(libversion / 1000000)
            minor = int((libversion - maj * 1000000) / 1000)
            host_capabilities_xml = self.get_host_capabilities(conn)
            host_cpu_topology = self.get_host_cpu_topology(host_capabilities_xml)
            totalCpuSockets = int(host_cpu_topology.get("sockets"))
            totalCpuCores = int(host_cpu_topology.get("cores")) * totalCpuSockets
            totalCpuThreads = int(host_cpu_topology.get("threads")) * totalCpuCores
            output[hypervisor_hostname] = {
                "name": hypervisor_hostname,
                "hostIdentifier": host_capabilities_xml.find("host/uuid").text,
                "type": conn.getType().lower(),
                "totalCpuSockets": totalCpuSockets,
                "totalCpuCores": totalCpuCores,
                "totalCpuThreads": totalCpuThreads,
                "cpuVendor": host_capabilities_xml.find("host/cpu/vendor").text,
                "cpuDescription": host_capabilities_xml.find("host/cpu/model").text,
                "cpuArch": host_capabilities_xml.find("host/cpu/arch").text,
                "cpuMhz": 0,
                "ramMb": int(self.get_host_memory(conn)),
                "vms": {},
                "optionalVmData": {},
                "os": "libvirt",
                "osVersion": f"{maj}.{minor}",
            }
            for domain in conn.listAllDomains(0):
                domain_name = domain.name()
                uuid = domain.UUIDString()
                output[hypervisor_hostname]["vms"][domain_name] = uuid
                output[hypervisor_hostname]["optionalVmData"][domain_name] = {}
                output[hypervisor_hostname]["optionalVmData"][domain_name][
                    "vmState"
                ] = self.VMSTATE.get(domain.info()[0], "unknown")
        except libvirt.libvirtError as err:
            self.log.error(err)
        return output

    @staticmethod
    def request_cred(credentials, user_data):
        """
        Authentication credentials to libvirt.

        :param credentials: list of credentials that libvirt would like to request
        :param user_data: list containing sasl_username and sasl_password
        :return: 0 on success and -1 on errors

        Reference:
        https://libvirt.org/docs/libvirt-appdev-guide-python/en-US/html/libvirt_application_development_guide_using_python-Connections.html#idm643
        """

        for credential in credentials:
            if credential[0] == libvirt.VIR_CRED_AUTHNAME:
                credential[4] = user_data[0]
            elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
                credential[4] = user_data[1]
            else:
                # error
                return -1
        return 0
