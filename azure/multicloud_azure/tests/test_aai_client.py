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

import mock
import unittest

from multicloud_azure.pub.utils import restcall


class TestAAIClient(unittest.TestCase):

    def setUp(self):
        self.view = restcall.AAIClient("vmware", "4.0")

    @mock.patch.object(restcall, "call_req")
    def test_get_vim(self, mock_call):
        mock_call.return_value = [0, '{"cloudOwner": "vmware"}']
        ret = self.view.get_vim(get_all=True)
        expect_ret = {"cloudOwner": "vmware"}
        self.assertEqual(expect_ret, ret)

    @mock.patch.object(restcall.AAIClient, "get_vim")
    @mock.patch.object(restcall, "call_req")
    def test_update_identity_url(self, mock_call, mock_getvim):
        mock_getvim.return_value = {}
        self.view.update_identity_url()
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_add_flavors(self, mock_call):
        flavors = {
            "flavors": [{
                "name": "m1.small",
                "id": "1",
                "vcpus": 1,
                "ram": 512,
                "disk": 10,
                "ephemeral": 0,
                "swap": 0,
                "is_public": True,
                "links": [{"href": "http://fake-url"}],
                "is_disabled": False
            }]
        }
        self.view.add_flavors(flavors)
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_add_flavors_with_hpa(self, mock_call):
        flavors = {
            "flavors": [{
                "name": "onap.small",
                "id": "1",
                "vcpus": 1,
                "ram": 512,
                "disk": 10,
                "ephemeral": 0,
                "swap": 0,
                "is_public": True,
                "links": [{"href": "http://fake-url"}],
                "is_disabled": False,
                "extra_specs": {},
            }]
        }
        self.view._get_ovsdpdk_capabilities = mock.MagicMock()
        self.view._get_ovsdpdk_capabilities.return_value = {}
        self.view.add_flavors(flavors)
        mock_call.assert_called_once()
