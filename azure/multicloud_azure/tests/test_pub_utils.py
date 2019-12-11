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

import unittest
import os
import mock
import json

from multicloud_azure.pub.utils.restcall import AAIClient
from multicloud_azure.pub.msapi import extsys
from multicloud_azure.pub.utils.timeutil import now_time
from multicloud_azure.pub.utils.fileutil import make_dirs, delete_dirs
from multicloud_azure.pub.utils.fileutil import download_file_from_http
from multicloud_azure.pub.vim.vimsdk.azure_credentials import ClientObj
from multicloud_azure.pub.exceptions import VimDriverAzureException

TENANT_ID = '123'
CLIENT = '456'
KEY = '789'

params = {
            'username': TENANT_ID,
            'password': KEY,
            'tenant_id': CLIENT
        }


class TestPub(unittest.TestCase):

    def test_client_obj(self):
        self.assertRaises(VimDriverAzureException,
                          ClientObj().get_client_obj, params)

    def test_time(self):
        fmt = "%Y-%m-%d %H:%M:%S"
        self.assertIsNotNone(now_time(fmt))

    def test_make_dirs(self):
        path = "/tmp/azure/azure/bin"
        self.assertEqual(os.makedirs(path, 0o777), make_dirs(path))

    def test_delete_dirs(self):
        path = "/tmp/azure/azure/bin"
        self.assertIsNone(delete_dirs(path))

    def test_download_file(self):
        url = "https://raw.githubusercontent.com/onapdemo/" \
              "onap-scripts/master/entrypoint/azure-rancher-server.sh"
        local_dir = "usr/local/bin"
        file_name = "azure"
        self.assertNotEquals(False, "usr/local/bin/azure",
                             download_file_from_http(url, local_dir,
                                                     file_name))

    def test_split_vim_to_owner_region(self):
        vim_id = 'ATT_eastus2'
        self.assertEquals(('ATT', 'eastus2'),
                          extsys.split_vim_to_owner_region(vim_id))

    @mock.patch.object(AAIClient, 'get_vim')
    def test_get_vim_id(self, mock_vim_info):
        vim_id = 'ATT_eastus2'
        json_file = os.path.join(os.path.dirname(
            __file__), 'aai_response.json')
        f = open(json_file).read()
        ret = json.loads(f)
        mock_vim_info.return_value = ret
        self.assertEqual(ret, extsys.get_vim_by_id(vim_id))
