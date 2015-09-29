Requires:

* For VMware: install python-pyvmomi from devel:languages:python
* For SUSECloud: install python-novaclient

Example:

List all installed modules with the required paramater:
```
$> scripts/gatherer --list-modules
{
    "SUSECloud": {
        "host": "",
        "module": "SUSECloud",
        "pass": "",
        "port": 5000,
        "proto": "https",
        "tenant": "openstack",
        "user": ""
    },
    "VMware": {
        "host": "",
        "module": "VMware",
        "pass": "",
        "port": 443,
        "user": ""
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
        "host": "vCenter.domain.top",
        "user": "admin",
        "pass": "secret",
        "port": 443
    },
    {
        "id": "mysusecloud",
        "module" : "SUSECloud",
        "proto" : "http",
        "host" : "susecloud.domain.top",
        "port" : 5000,
        "user" : "admin",
        "pass" : "secret",
        "tenant" : "openstack"
  }
]
```
-----------------------------------------

and call

```
$> scripts/gatherer --infile ./infile.json --outfile ./outfile.json
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
            "name": "d00-53-00-bd-a1-48.d3.mycloud.local",
            "os": "QEMU",
            "osVersion": 1004002,
            "ramMb": 32232,
            "totalCpuCores": 6,
            "totalCpuSockets": 1,
            "totalCpuThreads": 1,
            "vms": {}
        },
        "d00-53-00-bd-a3-c2.d3.mycloud.local": {
            "cpuArch": "x86_64",
            "cpuDescription": "Opteron_G3",
            "cpuMhz": 0,
            "cpuVendor": "AMD",
            "name": "d00-53-00-bd-a3-c2.d3.mycloud.local",
            "os": "QEMU",
            "osVersion": 1004002,
            "ramMb": 64487,
            "totalCpuCores": 6,
            "totalCpuSockets": 1,
            "totalCpuThreads": 1,
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
            "name": "10.0.0.1",
            "os": "VMware ESXi",
            "osVersion": "5.5.0",
            "ramMb": 65512,
            "totalCpuCores": 16,
            "totalCpuSockets": 2,
            "totalCpuThreads": 16,
            "vms": {
                "vCenter": "564d6d90-459c-2256-8f39-3cb2bd24b7b0"
            }
        },
        "10.0.0.2": {
            "cpuArch": "x86_64",
            "cpuDescription": "AMD Opteron(tm) Processor 4386",
            "cpuMhz": 3092.212639,
            "cpuVendor": "amd",
            "name": "10.0.0.2",
            "os": "VMware ESXi",
            "osVersion": "5.5.0",
            "ramMb": 65512,
            "totalCpuCores": 16,
            "totalCpuSockets": 2,
            "totalCpuThreads": 16,
            "vms": {
                "49737e0a-c9e6-4ceb-aef8-6a9452f67cb5": "4230c60f-3f98-2a65-f7c3-600b26b79c22",
                "5a2e4e63-a957-426b-bfa8-4169302e4fdb": "42307b15-1618-0595-01f2-427ffcddd88e",
                "NSX-gateway": "4230d43e-aafe-38ba-5a9e-3cb67c03a16a",
                "NSX-l3gateway": "4230b00f-0b21-0e9d-dfde-6c7b06909d5f",
                "NSX-service": "4230e924-b714-198b-348b-25de01482fd9"
            }
        }
    }
}
```
-----------------------------------------

References:

* http://www.orionscache.com/2012/05/adding-a-read-only-user-in-vcenter/

