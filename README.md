Requires:

* install python-pyvmomi from devel:languages:python
* install missing requirements: python-six and python-requests

Example:

Use as infile.json:
-----------------------------------------
```
[
  { "name" : "Cloud vCenter",
    "type" : "vCenter",
    "host" : "10.162.186.115",
    "port" : 443,
    "user" : "root",
    "pass" : "the password"
   }
]
```
-----------------------------------------

and call

```
$> scripts/gatherer --infile ./infile.json --outfile ./outfile.json
```

