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

from __future__ import absolute_import
from six import with_metaclass
import abc


# pylint: disable=abstract-class-not-used
class WorkerInterface(with_metaclass(abc.ABCMeta, object)):
    """
    Worker definition interface.
    """

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

        :return: Dictionary with parameters and default values
        """
        return dict()

    @abc.abstractmethod
    def run(self):
        """
        Run the worker.

        :return: Dictionary of the worker result.
        """
        return dict()

    @abc.abstractmethod
    def valid(self):
        """
        Return worker status, if the worker can function.

        :return: True, if module is operable.
        """
        return False

    def _validate_parameters(self, node):
        """
        Validate parameters.

        :param node: Dictionary with the node description.
        :return:
        """
        for param in self.parameters():
            if not node.get(param):
                raise AttributeError("Missing parameter or value '{0}' in infile".format(param))
