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

from azure.api_v2.api_router import v0_controller


class AzureController(rest.RestController):
    v0 = v0_controller.V0_Controller()


class APIController(rest.RestController):
    pass


# Pecan workaround for the dash in path.
pecan.route(APIController, "multicloud-azure", AzureController())


class RootController(object):
    api = APIController()
