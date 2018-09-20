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
import json
from rest_framework import status
from aria.cli.core import aria

from multicloud_azure.swagger.views.infra_workload.views import InfraWorkload
from multicloud_azure.swagger.views.infra_workload.views import GetStackView
from multicloud_azure.pub.aria.service import AriaServiceImpl


class InfraViewTest(unittest.TestCase):

    def setUp(self):
        self.fsv = InfraWorkload()

    def tearDown(self):
        pass

    def test_service_get_fail(self):
        req = mock.Mock()
        dict = {'infra-template': 'aria', 'infra-payload': json.dumps(
            {'name': 'abc', 'template_data': {'stack_name': 'stack'}})}
        req.data = dict
        resp = self.fsv.post(req, "abc", "def")
        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR,
                         resp.status_code)


class StackViewTest(unittest.TestCase):

    def setUp(self):
        self.fsv = GetStackView()

    def tearDown(self):
        pass

    def test_service_get_fail(self):

        class Request:
            def __init__(self, query_params):
                self.query_params = query_params
        req = Request({'k': 'v'})
        self.assertNotEqual(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            self.fsv.get(req, "abc", "def", 123))


class WorkoadViewTest(unittest.TestCase):

    def setUp(self):
        self.fsv = AriaServiceImpl()

    def tearDown(self):
        pass

    @mock.patch.object(AriaServiceImpl, 'deploy_service')
    def test_deploy_service(self, mock_service_info):

        class Service:
            def __init__(self, name, body, input, logger):
                self.name = name
                self.body = body
                self.input = input
                self.logger = logger
        s = Service("abc", "def", "ghi", "OK")
        mock_service_info.return_value = s
        service_op = AriaServiceImpl()
        self.assertNotEqual(200, service_op.deploy_service("a1", "b1", "c1",
                                                           "OK"))

    @mock.patch.object(AriaServiceImpl, 'install_template_private')
    @aria.pass_model_storage
    @aria.pass_resource_storage
    @aria.pass_plugin_manager
    @aria.pass_logger
    def test_install_template(self, mock_template_info, model_storage,
                              resource_storage, plugin_manager, logger):

        class Workload:
            def __init__(self, name, body):
                self.name = name
                self.body = body
        service = Workload("a", "w1")
        mock_template_info.return_value = service

        class Request:
            def __init__(self, query_params):
                self.query_params = query_params
        req = Request({'k': 'v'})
        self.assertNotEqual(200,
                            self.fsv.install_template_private(req, "a1", "b1",
                                                              model_storage,
                                                              resource_storage,
                                                              plugin_manager,
                                                              logger))

    @mock.patch.object(AriaServiceImpl, 'create_service')
    @aria.pass_model_storage
    @aria.pass_resource_storage
    @aria.pass_plugin_manager
    @aria.pass_logger
    def test_create_service(self, mock_template_info, model_storage,
                            resource_storage, plugin_manager, logger):
        class Workload:
            def __init__(self, id, name, input):
                self.id = id
                self.name = name
                self.input = input

        f1 = Workload(1, "a", "w1")
        f2 = Workload(2, "b", "w2")
        service = [f1, f2]
        mock_template_info.return_value = service

        class Request:
            def __init__(self, query_params):
                self.query_params = query_params

        req = Request({'k': 'v'})
        self.assertNotEqual(200,
                            self.fsv.create_service(req, 123, "a1", "b1",
                                                    model_storage,
                                                    resource_storage,
                                                    plugin_manager,
                                                    logger))

    @mock.patch.object(AriaServiceImpl, 'start_execution')
    @aria.pass_model_storage
    @aria.pass_resource_storage
    @aria.pass_plugin_manager
    @aria.pass_logger
    def test_start_execution(self, mock_template_info, model_storage,
                             resource_storage, plugin_manager, logger):
        class Workload:
            def __init__(self, status_id, execution_id, name, input):
                self.status_id = status_id
                self.execution_id = execution_id
                self.input = input
                self.name = name

        service = Workload(1, 2, "a", "w")
        mock_template_info.return_value = service

        class Request:
            def __init__(self, query_params):
                self.query_params = query_params

        req = Request({'k': 'v'})
        self.assertNotEqual(200,
                            self.fsv.start_execution(req, 123, 456, "a1", "b1",
                                                     model_storage,
                                                     resource_storage,
                                                     plugin_manager,
                                                     logger))

    def test_show_execution(self):
        service_op = AriaServiceImpl()
        self.assertNotEqual(200,
                            service_op.show_execution(123))
