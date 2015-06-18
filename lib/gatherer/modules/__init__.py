# Copyright (c) 2015 SUSE LLC. All Rights Reserved.
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

"""
Contains worker interface.
"""

import abc

# pylint: disable=abstract-class-not-used
class WorkerInterface(object):
    """
    Worker definition interface.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def set_node(self, node):
        """
        Set node values

        :return: void
        """

    @abc.abstractmethod
    def parameters(self):
        """
        Return required parameters with default values

        :return: Dictionary with paramters and default values
        """

    @abc.abstractmethod
    def run(self):
        """
        Run the worker.

        :return: Dictionary of the worker result.
        """

    @abc.abstractmethod
    def valid(self):
        """
        Return worker status, if the worker can function.

        :return: True, if module is operable.
        """
