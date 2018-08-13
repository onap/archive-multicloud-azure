# Copyright (c) 2017-2018 VMware, Inc.
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

from azure.pub.utils.restcall import AAIClient

logger = logging.getLogger(__name__)


def split_vim_to_owner_region(vim_id):
    split_vim = vim_id.split('_')
    cloud_owner = split_vim[0]
    cloud_region = "".join(split_vim[1:])
    return cloud_owner, cloud_region


def get_vim_by_id(vim_id):
    cloud_owner, cloud_region = split_vim_to_owner_region(vim_id)
    client = AAIClient(cloud_owner, cloud_region)
    ret = client.get_vim(get_all=True)
    ret['type'] = ret['cloud-type']
    ret['version'] = ret['cloud-region-version']
    ret['vimId'] = vim_id
    ret['name'] = vim_id
    ret['userName'] = ret['esr-system-info-list'][
        'esr-system-info'][0]['user-name']
    ret['password'] = ret['esr-system-info-list'][
        'esr-system-info'][0]['password']
    ret['tenant'] = ret['esr-system-info-list'][
        'esr-system-info'][0]['default-tenant']
    ret['url'] = ret['esr-system-info-list'][
        'esr-system-info'][0]['service-url']
    ret['domain'] = ret['esr-system-info-list'][
        'esr-system-info'][0]['cloud-domain']
    ret['cacert'] = ret['esr-system-info-list'][
        'esr-system-info'][0].get('ssl-cacert', "")
    ret['insecure'] = ret['esr-system-info-list'][
        'esr-system-info'][0].get('ssl-insecure', False)
    return ret
