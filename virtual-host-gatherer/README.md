Requires:

* For File: install python-urlgrabber
* For VMware: install python-pyvmomi from devel:languages:python
* For SUSECloud: install python-novaclient

Example:

List all installed modules with the required paramater:
```
$> scripts/virtual-host-gatherer --list-modules
{
    "SUSECloud": {
        "module": "SUSECloud",
        "hostname": "",
        "port": 5000,
        "username": "",
        "password": "",
        "protocol": "https",
        "tenant": "openstack"
    },
    "File": {
        "module": "File",
        "url": ""
    },
    "VMware": {
        "module": "VMware",
        "hostname": "",
        "port": 443,
        "username": "",
        "password": ""
    }
}
```

Additionally you can provide an *id* parameter. This will be used as key
for the output hash.

-----------------------------------------

Example input file (infile.json):
```
[
    {
        "id": "myvcenter",
        "module": "VMware",
        "hostname": "vCenter.domain.top",
        "username": "admin",
        "password": "secret",
        "port": 443
    },
    {
        "id": "mysusecloud",
        "module" : "SUSECloud",
        "protocol" : "http",
        "hostname" : "susecloud.domain.top",
        "port" : 5000,
        "username" : "admin",
        "password" : "secret",
        "tenant" : "openstack"
  }
]
```
-----------------------------------------

and call

```
$> scripts/virtual-host-gatherer --infile ./infile.json --outfile ./outfile.json
```

-----------------------------------------

Example output file (outfile.json):
```
{
    "mysusecloud": {
        "d00-53-00-bd-a1-48.d3.mycloud.local": {
            "cpuArch": "x86_64",
            "cpuDescription": "Opteron_G3",
            "cpuMhz": 0,
            "cpuVendor": "AMD",
            "hostIdentifier": "d00-53-00-bd-a1-48.d3.mycloud.local",
            "name": "d00-53-00-bd-a1-48.d3.mycloud.local",
            "os": "QEMU",
            "osVersion": 1004002,
            "ramMb": 32232,
            "totalCpuCores": 6,
            "totalCpuSockets": 1,
            "totalCpuThreads": 1,
            "type": "qemu",
            "vms": {}
        },
        "d00-53-00-bd-a3-c2.d3.mycloud.local": {
            "cpuArch": "x86_64",
            "cpuDescription": "Opteron_G3",
            "cpuMhz": 0,
            "cpuVendor": "AMD",
            "hostIdentifier": "d00-53-00-bd-a3-c2.d3.mycloud.local",
            "name": "d00-53-00-bd-a3-c2.d3.mycloud.local",
            "os": "QEMU",
            "osVersion": 1004002,
            "ramMb": 64487,
            "totalCpuCores": 6,
            "totalCpuSockets": 1,
            "totalCpuThreads": 1,
            "type": "qemu",
            "vms": {
                "instance-00000016": "e17366ac-e8e0-48e1-9af4-0044967733a0"
            }
        }
    },
    "myvcenter": {
        "10.0.0.1": {
            "cpuArch": "x86_64",
            "cpuDescription": "AMD Opteron(tm) Processor 4386",
            "cpuMhz": 3092.212727,
            "cpuVendor": "amd",
            "hostIdentifier": "'vim.HostSystem:host-182'",
            "name": "10.0.0.1",
            "os": "VMware ESXi",
            "osVersion": "5.5.0",
            "ramMb": 65512,
            "totalCpuCores": 16,
            "totalCpuSockets": 2,
            "totalCpuThreads": 16,
            "type": "vmware",
            "vms": {
                "vCenter": "564d6d90-459c-2256-8f39-3cb2bd24b7b0"
            },
            "optionalVmData": {
                "vCenter": {
                    "vmState": "stopped"
                }
            }
        },
        "10.0.0.2": {
            "cpuArch": "x86_64",
            "cpuDescription": "AMD Opteron(tm) Processor 4386",
            "cpuMhz": 3092.212639,
            "cpuVendor": "amd",
            "hostIdentifier": "'vim.HostSystem:host-183'",
            "name": "10.0.0.2",
            "os": "VMware ESXi",
            "osVersion": "5.5.0",
            "ramMb": 65512,
            "totalCpuCores": 16,
            "totalCpuSockets": 2,
            "totalCpuThreads": 16,
            "type": "vmware",
            "vms": {
                "49737e0a-c9e6-4ceb-aef8-6a9452f67cb5": "4230c60f-3f98-2a65-f7c3-600b26b79c22",
                "5a2e4e63-a957-426b-bfa8-4169302e4fdb": "42307b15-1618-0595-01f2-427ffcddd88e",
                "NSX-gateway": "4230d43e-aafe-38ba-5a9e-3cb67c03a16a",
                "NSX-l3gateway": "4230b00f-0b21-0e9d-dfde-6c7b06909d5f",
                "NSX-service": "4230e924-b714-198b-348b-25de01482fd9"
            },
            "optionalVmData": {
                "49737e0a-c9e6-4ceb-aef8-6a9452f67cb5": {
                    "vmState": "unknown"
                },
                "5a2e4e63-a957-426b-bfa8-4169302e4fdb": {
                    "vmState": "running"
                },
                "NSX-gateway": {
                    "vmState": "running"
                },
                "NSX-l3gateway": {
                    "vmState": "running"
                },
                "NSX-service": {
                    "vmState": "stopped"
                }
            }
        }
    }
}
```
-----------------------------------------

The 'type' of a hypervisor must be one of 'fully_virtualized', 'para_virtualized', 'qemu',
'vmware', 'hyperv', 'virtage' or 'virtualbox'

The value of 'hostIdentifier' must be unique for the given virtual host manager (vCenter or ESX/i instance)

References:

* http://www.orionscache.com/2012/05/adding-a-read-only-user-in-vcenter/

