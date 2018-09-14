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

import json
import os


def get_swagger_json_data():
    json_file = os.path.join(os.path.dirname(
        __file__), 'multivim.flavor.swagger.json')
    f = open(json_file)
    json_data = json.JSONDecoder().decode(f.read())
    f.close()
    # json_file = os.path.join(os.path.dirname(
    #     __file__), 'multivim.image.swagger.json')
    # f = open(json_file)
    # json_data_temp = json.JSONDecoder().decode(f.read())
    # f.close()
    # json_data["paths"].update(json_data_temp["paths"])
    # json_data["definitions"].update(json_data_temp["definitions"])
    json_data["basePath"] = "/api/multicloud-azure/v0/"
    json_data["info"]["title"] = "MultiVIM driver \
    of Microsoft Azure Service NBI"

    return json_data
