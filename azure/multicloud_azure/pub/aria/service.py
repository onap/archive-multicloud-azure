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
import json
import tempfile
import time
import os

from multicloud_azure.pub.aria import util
from aria.cli.core import aria
from aria.cli import utils
from aria.core import Core
from aria.cli import service_template_utils
from aria.storage import exceptions as storage_exceptions
from aria.utils import threading
from aria.orchestrator.workflow_runner import WorkflowRunner as Runner

LOG = logging.getLogger(__name__)

execution_state = util.SafeDict()


class AriaServiceImpl(object):

    def deploy_service(self, template_name, template_body, inputs, logger):

        service_template_name = template_name + "-template" + \
                        time.strftime('%Y%m%d%H%M%S')
        status = self.install_template_private(service_template_name,
                                               template_body)
        if (status[1] != 200):
            logger.error("Error while installing the service-template")
            return status[0], status[1]
        else:
            logger.info("service template {0} valiadated and stored".format(
                service_template_name))
        status = self.create_service(
            status, template_name + time.strftime('%Y%m%d%H%M%S'), inputs)
        if (status[1] != 200):
            return status[0], status[1]
        execution_id = time.strftime('%Y%m%d%H%M%S')
        thread = threading.ExceptionThread(target=self.start_execution,
                                           args=(status[2].id, execution_id,
                                                 inputs, 'install'))
        thread.start()
        return execution_id, 200

    @aria.pass_model_storage
    @aria.pass_resource_storage
    @aria.pass_plugin_manager
    @aria.pass_logger
    def install_template_private(self, service_template_name, template_body,
                                 model_storage,
                                 resource_storage,
                                 plugin_manager,
                                 logger):
        service_template_filename = "MainServiceTemplate.yaml"
        fileSp = template_body
        f = tempfile.NamedTemporaryFile(suffix='.csar',
                                        delete=False)
        f.write(fileSp.read())
        f.seek(fileSp.tell(), 0)
        service_template_path = f.name
        fileSp.close()
        file_path = service_template_utils.get(
            service_template_path, service_template_filename)

        core = Core(model_storage, resource_storage, plugin_manager)
        logger.info("service-template file {}".format(file_path))

        try:
            service_template_id = core.create_service_template(
                file_path,
                os.path.dirname(file_path),
                service_template_name)
        except storage_exceptions.StorageError as e:
            logger.error("storage exception")
            utils.check_overriding_storage_exceptions(
                e, 'service template', service_template_name)
            return e.message, 500
        except Exception as e:
            logger.error("catchall exception")
            return e.message, 500
        return "service template installed", 200, service_template_id

    @aria.pass_model_storage
    @aria.pass_resource_storage
    @aria.pass_plugin_manager
    @aria.pass_logger
    def create_service(self, template_id, service_name, input,
                       model_storage,
                       resource_storage,
                       plugin_manager,
                       logger):
        """
        Creates a service from the specified service template
        """
        input = input['sdnc_directives'] if'sdnc_directives'in input else None
        core = Core(model_storage, resource_storage, plugin_manager)
        service = core.create_service(template_id, input, service_name)
        logger.info("service {} created".format(service.name))
        return "service {} created".format(service.name), 200, service

    @aria.pass_model_storage
    @aria.pass_resource_storage
    @aria.pass_plugin_manager
    @aria.pass_logger
    def start_execution(self, service_id, execution_id, input, workflow_name,
                        model_storage,
                        resource_storage,
                        plugin_manager,
                        logger):
        """
        Start an execution for the specified service
        """
        input = input['sdnc_directives'] if'sdnc_directives'in input else None
        runner = Runner(model_storage, resource_storage, plugin_manager,
                        execution_id=execution_id,
                        service_id=service_id,
                        workflow_name=workflow_name,
                        inputs=input)

        service = model_storage.service.get(service_id)
        tname = '{}_{}_{}'.format(service.name, workflow_name,
                                  runner.execution_id)
        thread = threading.ExceptionThread(target=runner.execute,
                                           name=tname)
        thread.start()
        execution_state[str(runner.execution_id)] = [runner, thread]
        logger.info("execution {} started".format(runner.execution_id))
        return json.dumps({"id": runner.execution_id}), 202

    @aria.pass_model_storage
    @aria.pass_logger
    def show_execution(self, execution_id, model_storage, logger):
        """
        Return details of specified execution/Stack
        """
        try:
            execution = model_storage.execution.get(execution_id)
        except BaseException:
            return "Execution {} not found".format(execution_id), 404
        logger.info("showing details of execution id {}".format(execution_id))
        return json.dumps({"execution_id": execution_id,
                           "service_name": execution.service_name,
                           "service_template_name":
                               execution.service_template_name,
                           "workflow_name": execution.workflow_name,
                           "status": execution.status}), 200
