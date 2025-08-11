#!/usr/bin/python3

# SPDX-FileCopyrightText: 2015-2025 SUSE LLC
#
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=missing-module-docstring,deprecated-module

from __future__ import absolute_import
from distutils.core import setup

setup(
    name="virtual-host-gatherer",
    version="1.0.28",
    description="Gather virtual host and VM data",
    long_description="""\
Gather virtual host and VM data from different kind of hypervisors
""",
    author="Michael Calmer",
    author_email="mc@suse.com",
    url="http://www.suse.com",
    package_dir={"": "lib"},
    packages=["gatherer", "gatherer/modules"],
    scripts=["scripts/virtual-host-gatherer"],
    license="Apache-2.0",
)
