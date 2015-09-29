#!/usr/bin/env python
#
#

from __future__ import absolute_import
from distutils.core import setup

setup(name="gatherer",
      version="1.0.5",
      description="gather host and VM data",
      long_description="""\
Gather host and VM data from different kind of hypervisors
""",
      author='Michael Calmer',
      author_email='mc@suse.com',
      url='http://www.suse.com',
      package_dir={'': 'lib'},
      packages=['gatherer', 'gatherer/modules'],
      scripts=['scripts/gatherer'],
      license="Apache-2.0",)
