#
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

import sys

from setuptools import setup, find_packages

_PACKAGE_NAME = 'aria-extension-cloudify'
_PYTHON_SUPPORTED_VERSIONS = [(2, 6), (2, 7)]

if (sys.version_info[0], sys.version_info[1]) not in _PYTHON_SUPPORTED_VERSIONS:
    raise NotImplementedError('{0} Package support Python version 2.6 & 2.7 Only'
                              .format(_PACKAGE_NAME))

setup(
    name=_PACKAGE_NAME,
    version='4.1',
    description="Enable ARIA to utilize some of Cloudify's abilities, such as interfacing with AWS "
                "and Openstack.",
    author='Gigaspaces',
    author_email='cosmo-admin@gigaspaces.com',
    license='LICENSE',

    packages=find_packages(include=['adapters*']),
    install_requires=['apache-ariatosca'],
    entry_points={
        'aria_extension': [
            'adapter = adapters.extension'
        ]
    }
)
