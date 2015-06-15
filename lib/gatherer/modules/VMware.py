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
#
# http://pubs.vmware.com/vsphere-55/topic/com.vmware.wssdk.apiref.doc/right-pane.html

import logging
import atexit

from pyVim.connect import SmartConnect, Disconnect


class VMwareWorker(object):
    def __init__(self, node):
        self.log = logging.getLogger(__name__)
        for k in parameter():
            if k not in node:
                self.log.error("Missing parameter '%s' in infile", k)
                raise AttributeError("Missing parameter '%s' in infile" % k)

        self.host = node['host']
        self.port = node['port'] or 443
        self.user = node['user']
        self.password = node['pass']

    def run(self):
        self.log.info("Connect to %s:%s as user %s", self.host, self.port, self.user)
        si = SmartConnect(host=self.host,
                          user=self.user,
                          pwd=self.password,
                          port=int(self.port))
        if not si:
            self.log.error(
                "Could not connect to the specified host using specified "
                "username and password"
            )
            return

        atexit.register(Disconnect, si)

        content = si.RetrieveContent()
        output = dict()
        for child in content.rootFolder.childEntity:
            if hasattr(child, 'hostFolder'):
                # child is now a "datacenter"
                clusterList = child.hostFolder.childEntity
                for cluster in clusterList:
                    for host in cluster.host:
                        hname = host.summary.config.name.split()[0]
                        sockets = host.hardware.cpuInfo.numCpuPackages
                        cores = (host.hardware.cpuInfo.numCpuCores / sockets)
                        threads = (host.hardware.cpuInfo.numCpuThreads / cores / sockets)
                        ghz = (float(host.hardware.cpuInfo.hz) / float(1000 * 1000 * 1000))
                        ram = (int(host.hardware.memorySize / (1024 * 1024)))
                        output[hname] = {'name': hname,
                                         'os': host.summary.config.product.name,
                                         'osVersion': host.summary.config.product.version,
                                         'sockets': sockets,
                                         'cores': cores,
                                         'threads': threads,
                                         'ghz': ghz,
                                         'cpuVendor': host.hardware.cpuPkg[0].vendor,
                                         'cpuDescription': host.hardware.cpuPkg[0].description.strip(),
                                         'cpuArch': 'x86_64',
                                         'ram': ram,
                                         'vms': {}}
                        # If additional Hardeware info is wanted:
                        # print "pciDevice: %s" % host.hardware.pciDevice
                        for vm in host.vm:
                            # print "Guest: %s" % vm.config.name
                            # print "Guest State: %s" % vm.runtime.powerState
                            # print "Guest CPUs: %s" % vm.summary.config.numCpu
                            # print "Guest RAM: %s" % vm.summary.config.memorySizeMB
                            output[hname]['vms'][vm.config.name] = vm.config.uuid
        Disconnect(si)
        return output


def worker(node):
    return VMwareWorker(node)


def parameter():
    return {'host': '',
            'port': 443,
            'user': '',
            'pass': ''}
