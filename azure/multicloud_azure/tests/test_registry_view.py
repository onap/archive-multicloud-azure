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
from rest_framework import status
from multicloud_azure.swagger.views.registry.views import Registry
from multicloud_azure.swagger.views.registry.views import UnRegistry


from multicloud_azure.pub.msapi import extsys
from multicloud_azure.pub.utils.restcall import AAIClient
from multicloud_azure.pub.vim.vimapi.compute import OperateFlavors

VIM_INFO = {'cloud_extra_info': 1, 'username': 'user1',
            'password': '1234', 'default_tenant': 't1',
            'cloud_region_id': 'r1'}


class RegistryViewTest(unittest.TestCase):

    def setUp(self):
        self.reg = Registry()

    def tearDown(self):
        pass

    @mock.patch.object(OperateFlavors.OperateFlavors, 'list_flavors')
    @mock.patch.object(extsys, 'get_vim_by_id')
    def test_reg_get_flavors_view_fail(self, mock_vim_info, mock_flavors):
        mock_vim_info.return_value = VIM_INFO

        class Flavor:
            def __init__(self, id, name):
                self.id = id
                self.name = name

            def to_dict(self):
                return {"name": self.name, "id": self.id}

        f1 = Flavor(1, "f1")
        f2 = Flavor(2, "f2")
        flavors = [f1.to_dict(), f2.to_dict()]
        mock_flavors.return_value = flavors
        auth = {
            "subscription_id": "1",
            "username": "user",
            "password": "1234",
            "tenant_id": "t1",
            "region_id": "r1"}

        self.assertEqual(
            {'flavors': [{'id': 1, 'name': 'f1'},
                         {'id': 2, 'name': 'f2'}]},
            self.reg._get_flavors(auth))

    @mock.patch.object(OperateFlavors.OperateFlavors, 'list_flavors')
    @mock.patch.object(extsys, 'get_vim_by_id')
    def test_reg_get_flavors_view_fail2(self, mock_vim_info, mock_flavors):
        mock_vim_info.return_value = VIM_INFO
        mock_flavors.side_effect = Exception("something wrong")
        self.assertRaises(Exception, self.reg._get_flavors)


class UnRegistryViewTest(unittest.TestCase):

    def setUp(self):
        self.reg = UnRegistry()

    def tearDown(self):
        pass

    @mock.patch.object(AAIClient, 'delete_vim')
    @mock.patch.object(extsys, 'get_vim_by_id')
    def test_reg_delete_view(self, mock_vim_info, mock_del_vim):
        mock_vim_info.return_value = VIM_INFO

        class Request:
            def __init__(self, query_params):
                self.query_params = query_params
        req = Request({'k': 'v'})
        self.assertEqual(
            status.HTTP_204_NO_CONTENT,
            self.reg.delete(req, "vimid").status_code)
