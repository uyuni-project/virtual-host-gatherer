#!/usr/bin/env python
#
#

from distutils.core import setup

setup(name = "gatherer",
      version = "1.0.0",
      description = "gather host and VM data",
      long_description = """\
Gather host and VM data from different kind of hypervisors
""",
      author = 'Michael Calmer',
      author_email = 'mc@suse.com',
      url = 'http://www.suse.com',
      package_dir = {'': 'lib'},
      packages = ['gatherer'],
      scripts = ['scripts/gatherer'],
      license = "Apache-2.0",
      )
