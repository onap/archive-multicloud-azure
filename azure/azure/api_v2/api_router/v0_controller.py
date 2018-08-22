#    Copyright (c) 2018 Amdocs
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import pecan
from pecan import rest

from azure.api_v2.api_router import swagger_json


class V0_Controller(rest.RestController):

    def get(self, vim_id, tenant_id):
        """ Placeholder for sub controllers. """
        pecan.abort(405)

    def put(self, vim_id, tenant_id):
        """ Placeholder for sub controllers. """
        pecan.abort(405)

    def post(self, vim_id, tenant_id):
        """ Placeholder for sub controllers. """
        pecan.abort(405)

    def delete(self, vim_id, tenant_id):
        """ Placeholder for sub controllers. """
        pecan.abort(405)

    def get_all(self, vim_id, tenant_id):
        """ Placeholder for sub controllers. """
        pecan.abort(405)


pecan.route(V0_Controller, "swagger.json", swagger_json.SwaggerJson())


# Insert API stem from yaml files.
# controller_builder.insert_dynamic_controller(V0_Controller)
