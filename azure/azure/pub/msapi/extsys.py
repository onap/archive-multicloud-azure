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
    data = {
        'type': ret['cloud-type'],
        'version': ret['cloud-region-version'],
        'vimId': vim_id,
        'name': vim_id,
        'userName': ret['esr-system-info-list']['esr-system-info'][0]['user-name'],
        'password': ret['esr-system-info-list']['esr-system-info'][0]['password'],
        'tenant': ret['esr-system-info-list']['esr-system-info'][0]['default-tenant'],
        'url': ret['esr-system-info-list']['esr-system-info'][0]['service-url'],
        'domain': ret['esr-system-info-list']['esr-system-info'][0]['cloud-domain'],
        'cacert': ret['esr-system-info-list']['esr-system-info'][0].get('ssl-cacert', ""),
        'insecure': ret['esr-system-info-list']['esr-system-info'][0].get('ssl-insecure', False)
    }
    ret.update(data)
    return ret
