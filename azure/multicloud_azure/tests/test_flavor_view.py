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

import mock
from multicloud_azure.pub.msapi import extsys
from multicloud_azure.pub.vim.vimapi.compute import OperateFlavors
from multicloud_azure.swagger import compute_utils
from multicloud_azure.swagger.views.flavor.views import FlavorsView
from rest_framework import status

VIM_INFO = {'cloud_extra_info': 1, 'username': 'user1',
            'password': '1234', 'default_tenant': 't1',
            'cloud_region_id': 'r1'}


class FlavorViewTest(unittest.TestCase):

    def setUp(self):
        self.fsv = FlavorsView()

    def tearDown(self):
        pass

    @mock.patch.object(compute_utils, 'convert_vmsize_aai')
    @mock.patch.object(OperateFlavors.OperateFlavors, 'list_flavors')
    @mock.patch.object(extsys, 'get_vim_by_id')
    def test_flavors_get_fail(self, mock_vim_info,
                              mock_flavors, mock_formatter):
        mock_vim_info.return_value = VIM_INFO

        class Flavor:
            def __init__(self, id, name):
                self.id = id
                self.name = name
        f1 = Flavor(1, "f1")
        f2 = Flavor(2, "f2")
        flavors = [f1, f2]
        mock_flavors.return_value = flavors
        mock_formatter.return_value = flavors

        class Request:
            def __init__(self, query_params):
                self.query_params = query_params
        req = Request({'k': 'v'})
        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            self.fsv.get(req, "vimid").status_code)

    def test_vmsize_aai(self):
        expected = {
            'name': "abc",
            'vcpus': 1,
            'ram': 123,
            'disk': 1234
        }

        class VmSize:
            def __init__(self, name, number_of_cores, memory_in_mb,
                         os_disk_size_in_mb):
                self.name = name
                self.number_of_cores = number_of_cores
                self.memory_in_mb = memory_in_mb
                self.os_disk_size_in_mb = os_disk_size_in_mb
        v1 = VmSize("abc", 1, 123, 1234)
        self.assertEquals(expected, compute_utils.convert_vmsize_aai(v1))
