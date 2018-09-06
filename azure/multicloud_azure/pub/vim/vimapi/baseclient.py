# Copyright (c) 2018 Amdocs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

import logging

from multicloud_azure.pub.vim.vimsdk.azure_credentials import ClientObj
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient

LOG = logging.getLogger(__name__)


class baseclient(object):

    def __init__(self, **kwargs):
        self._compute = None
        self._resource = None

    def get_compute_client(self, params):
        if self._compute is not None:
            return self._compute
        credentials = ClientObj().get_client_obj(params)
        self._compute = ComputeManagementClient(
            credentials, params['subscription_id'])
        return self._compute

    def get_resource_client(self, params):
        if self._resource is not None:
            return self._resource
        credentials = ClientObj.get_client_obj(params)
        self._resource = ResourceManagementClient(
            credentials, params['subscription_id'])
        return self._resource
