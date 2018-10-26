#
# ============LICENSE_START===================================================
# Copyright (c) 2017 Cloudify.co.  All rights reserved.
# ===================================================================
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# ============LICENSE_END====================================================
#

from flask import Flask, request, jsonify
from flask_autodoc.autodoc import Autodoc
from aria import install_aria_extensions
from aria.cli.core import aria
from aria.utils import threading
from aria.orchestrator.workflow_runner import WorkflowRunner
from aria.orchestrator.workflows.executor.dry import DryExecutor
import util

version_id = "v0"
route_base = "/api/multicloud-azure/" + version_id + "/"
app = Flask("onap-aria-rest")
auto = Autodoc(app)

execution_state = util.SafeDict()


def main():
    install_aria_extensions()
    app.run(host='0.0.0.0', port=5000, threaded=True)


# start execution
@app.route(
    route_base +
    "services/<service_id>/executions/<workflow_name>",
    methods=['POST'])
@auto.doc()
@aria.pass_model_storage
@aria.pass_resource_storage
@aria.pass_plugin_manager
@aria.pass_logger
def start_execution(
        service_id,
        workflow_name,
        model_storage,
        resource_storage,
        plugin_manager,
        logger):
    """
    Start an execution for the specified service
    """
    body = request.json or {}
    executor = DryExecutor(
        ) if 'executor' in body and body['executor'] == 'dry' else None

    inputs = body['inputs'] if 'inputs' in body else None
    task_max_attempts = (body['task_max_attempts']
                         if 'task_max_attempts' in body else 30)
    task_retry_interval = (body['task_retry_interval']
                           if 'task_retry_interval' in body else 30)

    runner = WorkflowRunner(model_storage, resource_storage, plugin_manager,
                            service_id=service_id,
                            workflow_name=workflow_name,
                            inputs=inputs,
                            executor=executor,
                            task_max_attempts=task_max_attempts,
                            task_retry_interval=task_retry_interval)

    service = model_storage.service.get(service_id)
    tname = '{}_{}_{}'.format(service.name, workflow_name, runner.execution_id)
    thread = threading.ExceptionThread(target=runner.execute,
                                       name=tname)
    thread.start()
    execution_state[str(runner.execution_id)] = [runner, thread]
    logger.info("execution {} started".format(runner.execution_id))
    return jsonify({"id": runner.execution_id}), 202


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)
