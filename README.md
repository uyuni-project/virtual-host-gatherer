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

-----------------------------------------

Example input file (infile.json):
```
[
    {
        "module": "VMware",
        "host": "vCenter.domain.top",
        "user": "admin"
        "pass": "secret",
        "port": 443,
    },
    {
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

