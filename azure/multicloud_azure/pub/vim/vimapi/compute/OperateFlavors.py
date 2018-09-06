# Copyright (c) 2018 Amdocs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:

#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

import logging

from OperateCompute import OperateCompute
from multicloud_azure.swagger import compute_utils
logger = logging.getLogger(__name__)


class OperateFlavors(OperateCompute):

    def __init__(self, **kwargs):
        super(OperateFlavors, self).__init__(**kwargs)

    def list_flavors(self, data, **query):
        logger.info("Inside OperateFlavors.list_flavors ")
        flavors = self.request('virtual_machine_sizes', data, **query)
        flavors = flavors.list(data['region_id'])
        vmSizes = []
        for flavor in flavors:
            result = compute_utils.convert_vmsize_aai(flavor)
            vmSizes.append(result)
        return vmSizes
