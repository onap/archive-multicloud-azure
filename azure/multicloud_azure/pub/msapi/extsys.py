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

from multicloud_azure.pub.utils.restcall import AAIClient

logger = logging.getLogger(__name__)


def encode_vim_id(cloud_owner, cloud_region_id):
    '''
    compose vim_id by cloud_owner and cloud_region, make sure the vimid can be
    converted back when talking to AAI,etc.
    This is a backward compatibility design to reuse the existing
    implementation code
    :param cloud_owner:
    :param cloud_region:
    :return:
    '''

    # since the {cloud_owner}/{cloud_region_id"} is globally unique, the
    # concatenated one as below will be unique as well.

    vim_id = cloud_owner + "_" + cloud_region_id

    # other options:
    # 1, store it into cache so the decode and just look up the cache for
    # decoding
    # 2, use other delimiter in case that '_' was used by
    # cloud owner/cloud region id,
    # e.g. '.', '#', hence the decode need to try more than one time

    return vim_id


def decode_vim_id(vim_id):
    # m = re.search(r'^([0-9a-zA-Z-]+)_([0-9a-zA-Z_-]+)$', vim_id)
    # cloud_owner, cloud_region_id = m.group(1), m.group(2)
    return split_vim_to_owner_region(vim_id)

def split_vim_to_owner_region(vim_id):
    split_vim = vim_id.split('_')
    cloud_owner = split_vim[0]
    cloud_region = "".join(split_vim[1:])
    return cloud_owner, cloud_region


def get_vim_by_id(vim_id):
    cloud_owner, cloud_region = split_vim_to_owner_region(vim_id)
    client = AAIClient(cloud_owner, cloud_region)
    ret = client.get_vim(get_all=True)
    esrInfo = ret['esr-system-info-list']['esr-system-info'][0]
    data = {
        'type': ret['cloud-type'],
        'version': ret['cloud-region-version'],
        'cloud_extra_info': ret['cloud-extra-info'],
        'cloud_region_id': ret['cloud-region-id'],
        'name': vim_id,
        'username': esrInfo['user-name'],
        'password': esrInfo['password'],
        'default_tenant': esrInfo['default-tenant'],
        'url': esrInfo['service-url'],
        'domain': esrInfo['cloud-domain'],
        'cacert': esrInfo.get('ssl-cacert', ""),
        'insecure': esrInfo.get('ssl-insecure', False)
    }
    ret.update(data)
    return ret
